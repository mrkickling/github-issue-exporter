import os

import json
import pytest

from gh_issue_exporter import exporter, gh_utils


def path_relative_to_tests(filename):
    """Returns the absolute path of a file in ./tests

    Arguments:
    filename    - filename to append to tests path
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_dir, filename)


@pytest.fixture
def issues():
    """Fixture for mocked api responses"""
    path = path_relative_to_tests('example_data.json')
    with open(path, 'r', encoding='utf-8') as f:
        return [gh_utils.Issue.from_dict(i) for i in json.load(f)]


def test_exporter_is_gh_url():
    """Make sure GH urls are identified correctly"""
    gh_url = "https://github.com/mrkickling/github-issue-exporter"
    assert exporter.is_gh_url(gh_url)

    gh_url = "https://github.com/mrkickling/github-issue-exporter?param"
    assert exporter.is_gh_url(gh_url)

    not_gh_url = "https://google.com/mrkickling/github-issue-exporter"
    assert not exporter.is_gh_url(not_gh_url)

    not_gh_url = "https://github.com/mrkickling"
    assert not exporter.is_gh_url(not_gh_url)


def test_exporter_get_owner_from_gh_repo():
    """See that gh urls are parsed correctly"""

    gh_url = "https://github.com/mrkickling/github-issue-exporter"
    owner, repo = exporter.get_owner_and_repo_from_gh_url(gh_url)
    assert owner == 'mrkickling'
    assert repo == 'github-issue-exporter'

    gh_url = "https://github.com/mrkickling/github-issue-exporter?param"
    owner, repo = exporter.get_owner_and_repo_from_gh_url(gh_url)
    assert owner == 'mrkickling'
    assert repo == 'github-issue-exporter'


def test_exporter_save_to_file(issues):
    """Make sure we can save exported data to json/yml"""

    json_outpath = '/tmp/test.json'
    exporter.write_issues_to_file(json_outpath, issues)

    yaml_outpath = '/tmp/test.yaml'
    exporter.write_issues_to_file(yaml_outpath, issues)

    yml_outpath = '/tmp/test.yml'
    exporter.write_issues_to_file(yml_outpath, issues)
