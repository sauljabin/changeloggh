from pathlib import Path

import click
from rich import print_json
from rich.markdown import Markdown
from rich.console import Console

from changeloggh import VERSION
from changeloggh.changelog import (
    CHANGELOG_PATH,
    CHANGELOG_LOCK_PATH,
    empty_changelog,
    load_changelog,
)


@click.version_option(VERSION)
@click.group()
def main():
    pass


@main.command("init")
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Force saving an empty CHANGELOG file.",
    show_default=True,
)
@click.argument("repository", nargs=1)
def init(force, repository):
    """
    Initialize a CHANGELOG.md file.

    \b
    REPOSITORY  GitHub Repository.
                (ex: https://github.com/sauljabin/changeloggh).
    """

    if not force:
        for str_path in [CHANGELOG_PATH, CHANGELOG_LOCK_PATH]:
            path = Path(str_path)
            if path.exists():
                print(f"{str_path} file already exists. Use --force to override the file.")
                exit(1)

    changelog = empty_changelog(repository)
    changelog.save()


@main.command("print")
@click.option(
    "--format",
    type=click.Choice(["rich", "text", "json"], case_sensitive=False),
    default="rich",
    help="What format to use.",
    show_default=True,
)
def print_changelog(format):
    """
    Print changelog file.
    """

    cl = load_changelog()

    match format:
        case "rich":
            console = Console()
            console.print(Markdown(cl.to_string()))
        case "text":
            print(cl.to_string())
        case "json":
            print_json(cl.to_json(), indent=4)


if __name__ == "__main__":
    main()
