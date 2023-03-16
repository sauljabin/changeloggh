# changeloggh

<a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/-python-success?logo=python&logoColor=white"></a>
<a href="https://github.com/sauljabin/changeloglg"><img alt="GitHub" src="https://img.shields.io/badge/status-active-brightgreen"></a>
<a href="https://github.com/sauljabin/changeloglg/blob/main/LICENSE"><img alt="MIT License" src="https://img.shields.io/github/license/sauljabin/changeloglg"></a>
<a href="https://github.com/sauljabin/changeloglg/actions"><img alt="GitHub Actions" src="https://img.shields.io/github/actions/workflow/status/sauljabin/changeloglg/main.yml?branch=main"></a>
<a href="https://app.codecov.io/gh/sauljabin/changeloglg"><img alt="Codecov" src="https://img.shields.io/codecov/c/github/sauljabin/changeloglg"></a>
<a href="https://pypi.org/project/changeloglg"><img alt="Python Versions" src="https://img.shields.io/pypi/pyversions/changeloglg"></a>
<a href="https://pypi.org/project/changeloglg"><img alt="Version" src="https://img.shields.io/pypi/v/changeloglg"></a>
<a href="https://libraries.io/pypi/changeloglg"><img alt="Dependencies" src="https://img.shields.io/librariesio/release/pypi/changeloglg"></a>
<a href="https://pypi.org/project/changeloglg"><img alt="Platform" src="https://img.shields.io/badge/platform-linux%20%7C%20osx-blueviolet"></a>


`changeloggh` is a command line tool 
that generates and administrate changelog files for GitHub
according to https://keepachangelog.com/en/1.1.0/.

# Installation

Install with pip:
```sh
pip install changeloggh
```

Upgrade with pip:
```sh
pip install --upgrade changeloggh
```

## Usage

> Alias clgh

Help:
```sh
changeloggh --help
```

Version:
```sh
changeloggh --version
```

## Development

Installing poetry:
```sh
pip install poetry
```

Installing development dependencies:
```sh
poetry install
```

Running unit tests:
```sh
poetry run python -m scripts.tests
```

Applying code styles:
```sh
poetry run python -m scripts.styles
```

Running code analysis:
```sh
poetry run python -m scripts.analyze
```

Running code coverage:
```sh
poetry run python -m scripts.coverage
```

Running cli using `poetry`:
```sh
poetry run changeloggh
```

## Release a new version

> Check https://python-poetry.org/docs/cli/#version

```shell
poetry version <major|minor|patch>
git add -A
git commit -m "bumping version to $(poetry version -s)"
git tag $(poetry version -s)
git push origin main
git push --tags
```
