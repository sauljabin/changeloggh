# changeloggh

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
