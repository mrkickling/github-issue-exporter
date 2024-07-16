"""Exporter for Github Issues"""
import json
import logging

import requests

from .gh_utils import (
    create_gh_api_issues_url,
    get_owner_and_repo_from_gh_url,
    is_gh_url, Issue
)

from .exporter import get_gh_issues

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def verify_response(res: requests.Response):
    """Raise if error"""
    if res.status_code >= 300:
        raise requests.HTTPError(res.json())


def import_issues_to_repo(
        owner: str, repo: str, token: str, issues: list[Issue]
    ) -> None:
    """Import github issues using GH API to given owner + repo"""

    headers = {
        'Authorization': f'Bearer {token}',
        'X-GitHub-Api-Version': '2022-11-28' 
    }

    issues_url = create_gh_api_issues_url(owner, repo)
    for issue in issues:
        res = requests.post(
            issues_url, json=issue.to_dict(), headers=headers, timeout=30
        )
        verify_response(res)
        logger.info("Imported issue %s", issue.title)


def load_export_file(filename: str) -> list[Issue]:
    """Read issues and prs from json file, convert and return"""
    with open(filename, 'r', encoding='utf-8') as f:
        export_file = json.load(f)
        issues = [
            Issue.from_dict(issue) for issue in export_file.get('issues', [])
        ]
        return issues


def run_import(
        repo_url: str,
        export_file: str,
        token: str,
        verbose=False,
    ) -> None:
    """Import issues from export file to repository"""

    if verbose:
        logger.setLevel(logging.DEBUG)

    owner = ""
    repo_name = ""
    if is_gh_url(repo_url):
        owner, repo_name = get_owner_and_repo_from_gh_url(repo_url)
    else:
        raise ValueError(f"{repo_url} is not a URL to a github repository")

    # Fetch the issues and PRs from remote and from export file
    remote_issues = get_gh_issues(owner, repo_name)
    local_issues = load_export_file(export_file)
    logger.info(
        "Found %s issues in GH repo %s", len(remote_issues), repo_name)
    logger.info(
        "Found %s issues in file %s", len(local_issues), export_file)

    # Find issues to actually import and import them
    missing_issues = set(local_issues) - set(remote_issues)
    logger.info(
        "%s issues to import", len(missing_issues))
    import_issues_to_repo(owner, repo_name, token, missing_issues)

    logger.info(
        "Imported %s issues", len(missing_issues)
    )
