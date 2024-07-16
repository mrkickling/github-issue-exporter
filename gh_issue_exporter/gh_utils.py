from __future__ import annotations
from dataclasses import dataclass, field

GH_BASE_URL = "https://github.com/"
GH_BASE_API_URL = "https://api.github.com"


@dataclass(frozen=True)
class Issue:
    """Representation of a GH issue"""
    title: str
    body: str
    labels: list = field(compare=False)
    state: str

    @classmethod
    def from_dict(cls, dictionary: dict) -> Issue:
        """Convert dict to Issue"""
        return cls(
            dictionary.get('title'),
            dictionary.get('body'),
            dictionary.get('labels'),
            dictionary.get('state')
        )

    def to_dict(self) -> dict:
        """Convert Issue to dict"""
        return {
            'title': self.title,
            'body': self.body,
            'labels': self.labels,
            'state': self.state,
        }


@dataclass(frozen=True)
class PullRequest:
    """Representation of a GH PR"""
    title: str
    body: str
    labels: list = field(compare=False)
    state: str
    head: str
    base: str

    @classmethod
    def from_dict(cls, dictionary: dict) -> Issue:
        """Convert dict to Issue"""
        return cls(
            dictionary.get('title'),
            dictionary.get('body'),
            dictionary.get('labels'),
            dictionary.get('state'),
            dictionary.get('head'),
            dictionary.get('base')
        )

    def to_dict(self) -> dict:
        """Convert Issue to dict"""
        return {
            'title': self.title,
            'body': self.body,
            'labels': self.labels,
            'state': self.state,
            'head': self.head,
            'base': self.base,
        }


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
