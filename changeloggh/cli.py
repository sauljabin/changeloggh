from pathlib import Path
from typing import List

import click
from rich import print_json
from rich.console import Console
from rich.markdown import Markdown

from changeloggh import VERSION
from changeloggh.changelog import (
    CHANGELOG_PATH,
    CHANGELOG_LOCK_PATH,
    empty_changelog,
    load_changelog,
    ChangeType,
    BumpRule,
    parse_changelog,
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
def init(force: bool, repository: str):
    """
    Initialize a CHANGELOG.md file.

    \b
    REPOSITORY  GitHub Repository.
                (ex.: https://github.com/sauljabin/changeloggh).
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
def print_changelog(format: str):
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


@main.command("added")
@click.argument("entries", nargs=-1)
def added(entries: List[str]):
    """
    Add new entries to "Added" change type.

    ex.: changeloggh added "New feature" "New validation added".

    \b
    ENTRIES  List of entries.
    """
    add_entry(ChangeType.Added, entries)


@main.command("changed")
@click.argument("entries", nargs=-1)
def changed(entries: List[str]):
    """
    Add new entries to "Changed" change type.

    ex.: changeloggh changed "Size was changed" "Change auth method".

    \b
    ENTRIES  List of entries.
    """
    add_entry(ChangeType.Changed, entries)


@main.command("deprecated")
@click.argument("entries", nargs=-1)
def deprecated(entries: List[str]):
    """
    Add new entries to "Deprecated" change type.

    ex.: changeloggh deprecated "Option force" "Add method".

    \b
    ENTRIES  List of entries.
    """
    add_entry(ChangeType.Deprecated, entries)


@main.command("fixed")
@click.argument("entries", nargs=-1)
def fixed(entries: List[str]):
    """
    Add new entries to "Fixed" change type.

    ex.: changeloggh fixed "Error when loading" "Fix panel size".

    \b
    ENTRIES  List of entries.
    """
    add_entry(ChangeType.Fixed, entries)


@main.command("removed")
@click.argument("entries", nargs=-1)
def removed(entries: List[str]):
    """
    Add new entries to "Removed" change type.

    ex.: changeloggh removed "Remove unnecessary code" "Remove deprecated function".

    \b
    ENTRIES  List of entries.
    """
    add_entry(ChangeType.Removed, entries)


@main.command("security")
@click.argument("entries", nargs=-1)
def security(entries: List[str]):
    """
    Add new entries to "Security" change type.

    ex.: changeloggh security "Add security patch" "Update dependencies".

    \b
    ENTRIES  List of entries.
    """
    add_entry(ChangeType.Security, entries)


def add_entry(change_type, entries):
    path = Path(CHANGELOG_LOCK_PATH)
    if not path.exists():
        print(f'{CHANGELOG_LOCK_PATH} file does not exist. Use "init" command to initialize.')
        exit(1)
    cl = load_changelog()
    for entry in entries:
        cl.add(change_type, entry)
    cl.save()


@main.command("update")
def update():
    """
    Update the CHANGELOG.md file.
    """
    path = Path(CHANGELOG_LOCK_PATH)
    if not path.exists():
        print(f'{CHANGELOG_LOCK_PATH} file does not exist. Use "init" command to initialize.')
        exit(1)
    cl = load_changelog()
    cl.save()


@main.command("latest")
def latest():
    """
    Print latest (current) version.
    """
    path = Path(CHANGELOG_LOCK_PATH)
    if not path.exists():
        print(f'{CHANGELOG_LOCK_PATH} file does not exist. Use "init" command to initialize.')
        exit(1)
    cl = load_changelog()
    print(cl.latest())


@main.command("bump")
@click.argument(
    "rule", type=click.Choice(["major", "minor", "patch"], case_sensitive=False), nargs=1
)
def bump(rule: str):
    """
    Bump to a next version.
    """
    try:
        cl = load_changelog()
        new_version = cl.bump(BumpRule[rule])
        cl.save()
        print(new_version)
    except Exception as ex:
        print(
            f"{str(ex)}. Use {{added|changed|deprecated|removed|fixed|security}} commands to add"
            " changes."
        )
        exit(1)


@main.command("release")
@click.argument("version", nargs=1)
def release(version: str):
    """
    Release a specific version.
    """
    try:
        cl = load_changelog()
        new_version = cl.release(version)
        cl.save()
        print(new_version)
    except Exception as ex:
        print(
            f"{str(ex)}. Use {{added|changed|deprecated|removed|fixed|security}} commands to add"
            " changes."
        )
        exit(1)


@main.command("import")
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help='Force to override the "changelog.lock" file.',
    show_default=True,
)
def import_md(force: bool):
    """
    Import a MD file.
    """

    if not force:
        path = Path(CHANGELOG_LOCK_PATH)
        if path.exists():
            print(f"{CHANGELOG_LOCK_PATH} file already exists. Use --force to override the file.")
            exit(1)

    cl = parse_changelog()
    cl.save()
    print_json(cl.to_json(), indent=4)


if __name__ == "__main__":
    main()
