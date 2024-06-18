# changeloggh

<a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/-python-success?logo=python&logoColor=white"></a>
<a href="https://github.com/sauljabin/changeloggh"><img alt="GitHub" src="https://img.shields.io/badge/status-active-brightgreen"></a>
<a href="https://github.com/sauljabin/changeloggh/blob/main/LICENSE"><img alt="MIT License" src="https://img.shields.io/github/license/sauljabin/changeloggh"></a>
<a href="https://github.com/sauljabin/changeloggh/actions"><img alt="GitHub Actions" src="https://img.shields.io/github/actions/workflow/status/sauljabin/changeloggh/main.yml?branch=main"></a>
<a href="https://app.codecov.io/gh/sauljabin/changeloggh"><img alt="Codecov" src="https://img.shields.io/codecov/c/github/sauljabin/changeloggh"></a>
<a href="https://pypi.org/project/changeloggh"><img alt="Python Versions" src="https://img.shields.io/pypi/pyversions/changeloggh"></a>
<a href="https://pypi.org/project/changeloggh"><img alt="Version" src="https://img.shields.io/pypi/v/changeloggh"></a>
<a href="https://libraries.io/pypi/changeloggh"><img alt="Dependencies" src="https://img.shields.io/librariesio/release/pypi/changeloggh"></a>
<a href="https://pypi.org/project/changeloggh"><img alt="Platform" src="https://img.shields.io/badge/platform-linux%20%7C%20osx-blueviolet"></a>

`changeloggh` is a command line tool
to generate and administrate changelog files for GitHub
according to https://keepachangelog.com/en/1.1.0/.

<p align="center">
<img width="45%" src="https://raw.githubusercontent.com/sauljabin/changeloggh/main/screenshots/md.png">
<img width="45%" src="https://raw.githubusercontent.com/sauljabin/changeloggh/main/screenshots/json.png">
</p>

# Installation

```sh
pipx install changeloggh
```

Upgrade with pip:
```sh
pipx upgrade changeloggh
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

Init CHANGELOG:
```shell
changeloggh init <GitHub Repo>
```

Add changes:
```sh
changeloggh <added|changed|deprecated|removed|fixed|security> "entry 1" "entry 2" ...
```

Bump version:
```shell
changeloggh bump <major|minor|patch>
```

Release version:
```shell
changeloggh release <version>
```

Import MD:
```shell
changeloggh import
```

Print current version:
```shell
changeloggh latest
```

Print CHANGELOG:
```shell
changeloggh print --format <rich|json|text>
```

## Development

Installing poetry:
```sh
pipx install poetry
```

Installing development dependencies:
```sh
poetry install
```

Installing pre-commit:
```sh
poetry run pre-commit install
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
poetry run python -m scripts.bump --help
poetry run python -m scripts.bump <major|minor|patch>
```

## Why a lock file?

A lot of tools (like `yarn`, `npm`, `poetry` ,etc) use `lock files` to
ensures that installations remain identical and reproducible
across systems. A `lock files` saves important metadata, so that is why
`changeloggh` is using this approach. The `changelog.lock` file
saves and structures changelog data in a json format.
It's highly recommended to commit the `changelog.lock` file into your repository.

## Limitations

- Does not support other format besides `semver` `major.minor.patch`, ex.: 1.1.1.
- It needs a `changelog.lock`.

## Alternatives

- [changelog-cli](https://github.com/mc706/changelog-cli)
