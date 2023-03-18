from pathlib import Path

import click

from changeloggh import VERSION

CHANGELOG_PATH = "./CHANGELOG.md"

CHANGELOG_TEMPLATE = """
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.1] - 2023-03-17

### Added

- Initial setup

[unreleased]: https://github.com/sauljabin/changeloggh/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/sauljabin/changeloggh/releases/tag/v0.0.1
"""


@click.version_option(VERSION)
@click.group()
def main():
    pass


@main.command("init")
@click.option("--force", is_flag=True, default=False, help="Force saving an empty CHANGELOG file.")
def init(force: bool):
    path = Path(CHANGELOG_PATH)

    if path.exists() and not force:
        print(f"{CHANGELOG_PATH} file already exists")
        exit(1)

    with open(path, "w") as file:
        file.write(CHANGELOG_TEMPLATE)


if __name__ == "__main__":
    main()
