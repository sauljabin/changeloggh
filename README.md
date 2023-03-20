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

## Why a lock file?

A lot of tools (like `yarn`, `npm`, `poetry` ,etc) use `lock files` to
ensures that installations remain identical and reproducible
across systems. A `lock files` saves important metadata, tha is why
`changeloggh` is using this approach. The `changelog.lock` file
saves and structures changelog data in a json format.
It's highly recommended to commit the `changelog.lock` file into your repository.

## Limitations

- Does not support other format besides `semver` `major.minor.patch`, ex: 1.1.1.
- It needs a `changelog.lock`.

## Alternatives

- [changelog-cli](https://github.com/mc706/changelog-cli)

# TODO

- add command for adding new change
- import from md
- readme
- bump script
