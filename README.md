# Github Issue Exporter

Do you want a backup of your Github export?

This is your chance to do it!

## Installation

### Dependencies
Only dependency is the python library `requests`

Either clone the repo and install with `pip install .` or install with pip:

`pip install gh-issue-exporter`

See PyPi page: https://pypi.org/project/gh-issue-exporter/

### Local install

1. Clone repo
2. `python3 -m virtualenv venv` + `source venv/bin/activate`
3. pip install .

## Usage

Use the handy CLI provided by GH Issue Export.

### Exporting issues from a Github repository

`gh-issue-exporter export <REPO_URL>`

ex.

`gh-issue-exporter export https://github.com/mal-lang/mal-toolbox/`

This creates a JSON file with issues called 'mal-toolbox.json' in the same directory as it was run.

To select outfile name, use the o-flag: `-o <outfile>`

To export pull requests as well:

`gh-issue-exporter export https://github.com/mal-lang/mal-toolbox/ --pull_requests [-p]`


### Importing issues from an issue file to a repository

#### Preparation

- For gh-issue-exporter to be able to create issues, you need to use a Github Token.
    - Visit: https://github.com/settings/tokens
    - Click 'Generate New Token'
    - Authenticate if needed
    - Give the token access to the repository you want to import TO
    - Give read and write access to 'Issues'

To import issues from an existing issues file, run:

`gh-issue-exporter import <REPO_URL> <ISSUE_FILE> <TOKEN>`

ex.

`gh-issue-exporter import https://github.com/mrkickling/github-issue-exporter mal-toolbox.json github_[redacted]`

