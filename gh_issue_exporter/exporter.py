"""Exporter for Github Issues"""
import json
import logging
from typing import Optional

import requests

from .gh_utils import Issue, PullRequest

GH_BASE_URL = "https://github.com/"
GH_BASE_API_URL = "https://api.github.com"

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_owner_and_repo_from_gh_url(url: str) -> tuple[str, str]:
    """Extract the owner and repo name from a github repo url"""

    # Remove possible parameters and trailing slash
    url_no_params = url.split("?")[0].rstrip("/")

    # '<owner>/<repo>' will be at end of the URL
    return url_no_params.split("/")[-2:]


def is_gh_url(url: str) -> bool:
    """Understand if given string is a github repo url"""
    # Github repo url has at least 4 slashes, but we allow for trailing slash
    return url.startswith(GH_BASE_URL) and 4 <= url.count("/") <= 5


def create_gh_api_issues_url(owner: str, repo: str) -> str:
    """Craft a url that can be used to fetch issues for given owner + repo"""
    return f"{GH_BASE_API_URL}/repos/{owner}/{repo}/issues"


def create_gh_api_pulls_url(owner: str, repo: str) -> str:
    """Craft a url that can be used to fetch PRs for given owner + repo"""
    return f"{GH_BASE_API_URL}/repos/{owner}/{repo}/pulls"


def next_page_gh_api(res) -> str:
    """Pagination of api results, find next link"""
    url = ""
    next_link = res.headers.get('link')  # pagination

    next_page_exists = (
        next_link and next_link.find('rel=\"next\"') > -1
    )
    if next_page_exists:
        url = next_link.split('>;')[0].replace('<', '')
    return url


def get_gh_issues(owner: str, repo: str) -> list[Issue]:
    """Get github issues from the Github API for given owner + repo"""

    def verify_response(res):
        if isinstance(res, dict) and json_response.get('status') == '404':
            raise LookupError(f"Could not find github repo {repo}")

    issues_url = create_gh_api_issues_url(owner, repo)

    issues = []
    while issues_url:
        # Get issues for current issues_url
        res = requests.get(issues_url, timeout=30)
        json_response = res.json()
        verify_response(json_response)
        issues += [Issue.from_dict(issue) for issue in json_response]
        issues_url = next_page_gh_api(res)

    return issues


def get_gh_pull_requests(owner: str, repo: str) -> list[PullRequest]:
    """Get PRs from Github API for given owner + repo"""

    def verify_response(res):
        if isinstance(res, dict) and json_response.get('status') == '404':
            raise LookupError(f"Could not find github repo {repo}")

    pulls_url = create_gh_api_pulls_url(owner, repo)

    pull_requests = []
    while pulls_url:
        # Get PRs for current pulls_url
        res = requests.get(pulls_url, timeout=30)
        json_response = res.json()
        verify_response(json_response)
        pull_requests += [PullRequest.from_dict(pr) for pr in json_response]
        pulls_url = next_page_gh_api(res)

    return pull_requests


def write_export_to_json_file(filename: str, issues: list) -> None:
    """Write issues to json file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(issues, f)


def write_issues_to_file(filename: str, export: dict) -> None:
    """Write issues to file with chosen file format"""

    if not export:
        logger.warning("Nothing to export found, not writing anything")
        return

    serialized = {}
    serialized['issues'] = []
    serialized['prs'] = []

    for issue in export.get('issues'):
        serialized['issues'].append(issue.to_dict())
    for pr in export.get('prs'):
        serialized['prs'].append(pr.to_dict())

    write_export_to_json_file(filename, serialized)
    logger.info("Export written to file %s", filename)


def run_export(
        repo_url: str,
        export_prs: bool = False,
        verbose: bool = False,
        outfile: Optional[str] = None
    ) -> None:
    """Fetch issues and optionally PRs from a repo and export to a file"""

    if verbose:
        logger.setLevel(logging.DEBUG)

    owner = ""
    repo_name = ""
    if is_gh_url(repo_url):
        owner, repo_name = get_owner_and_repo_from_gh_url(repo_url)
    else:
        raise ValueError(f"{repo_url} is not a URL to a github repository")

    export = {}

    # Fetch the issues
    export['issues'] = get_gh_issues(owner, repo_name)
    logger.info(
        "Found %s issues in GH repo %s",
        len(export['issues']), repo_name
    )

    if export_prs:
        export['prs'] = get_gh_pull_requests(owner, repo_name)
        logger.info(
            "Found %s PRs in GH repo %s",
            len(export['prs']), repo_name
        )

    # Save the issues to a file
    outfile = outfile or (repo_name + ".json")
    write_issues_to_file(outfile, export)
