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
    if res.status_code >= 300:
        raise requests.HTTPError(res.json())


def import_issues_to_repo(
        owner: str, repo: str, token: str, issues: list[Issue]
    ) -> None:
    """Get github issues from the Github API for given owner + repo"""

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


def load_issues_from_json(filename: str) -> list[Issue]:
    """Read issues from json file, convert and return"""
    with open(filename, 'r', encoding='utf-8') as f:
        issues = [Issue.from_dict(issue) for issue in json.load(f)]
        return issues


def import_issues(
        repo_url: str,
        issues_file: str,
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

    # Fetch the issues
    remote_issues = get_gh_issues(owner, repo_name)
    local_issues = load_issues_from_json(issues_file)
    logger.info(
        "Found %s issues in GH repo %s", len(remote_issues), repo_name)
    logger.info(
        "Found %s issues in file %s", len(local_issues), issues_file)

    missing_issues = set(local_issues) - set(remote_issues)
    logger.info(
        "%s issues to import", len(missing_issues))
    import_issues_to_repo(owner, repo_name, token, missing_issues)

    logger.info(
        "Importing %s missing issues", len(missing_issues))
