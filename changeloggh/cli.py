from pathlib import Path
from typing import List

import cloup
from cloup import Section
from rich import print_json
from rich.console import Console
from rich.markdown import Markdown
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import MarkdownViewer, Footer

from changeloggh import VERSION
from changeloggh.changelog import (
    CHANGELOG_PATH,
    CHANGELOG_LOCK_PATH,
    empty_changelog,
    load_changelog,
    ChangeType,
    BumpRule,
    parse_changelog,
    JSON_INDENT,
)

START = Section("Start a changelog file")
ADD = Section("Add new entries")
EXAMINE = Section("Examine changelog")
RELEASE = Section("Release version")


@cloup.version_option(VERSION)
@cloup.group()
def main():
    """
    changeloggh is a command line tool to generate and administrate
    changelog files for GitHub according to https://keepachangelog.com/en/1.1.0/.

    changeloggh uses a changelog.lock file, it saves and structures changelog data in json format.
    It's highly recommended to commit the changelog.lock file into your repository.
    """
    pass


@main.command("init", section=START)
@cloup.option(
    "--force",
    is_flag=True,
    default=False,
    help="Force saving an empty CHANGELOG file.",
    show_default=True,
)
@cloup.argument("repository", nargs=1)
def init(force: bool, repository: str):
    """
    Initialize a CHANGELOG.md file.

    ex.: changeloggh init https://github.com/sauljabin/changeloggh

    \b
    REPOSITORY  GitHub Repository.
    """

    if not force:
        for str_path in [CHANGELOG_PATH, CHANGELOG_LOCK_PATH]:
            path = Path(str_path)
            if path.exists():
                print(f"{str_path} file already exists. Use --force to override the file.")
                exit(1)

    changelog = empty_changelog(repository)
    changelog.save()


@main.command("live", section=EXAMINE)
def live():
    """
    Show a live version of the CHANGELOG.md file.
    """

    cl = load_changelog()

    class MarkdownApp(App):
        BINDINGS = [
            Binding(key="ctrl+q", action="quit", description="Quit Viewer"),
            Binding(
                key="ctrl+t", action="toggle_table_of_contents", description="Toggle Navigation"
            ),
        ]

        def compose(self) -> ComposeResult:
            yield MarkdownViewer(cl.to_string(), show_table_of_contents=False)
            yield Footer()

        def action_toggle_table_of_contents(self) -> None:
            markdown_viewer = self.query_one(MarkdownViewer)
            markdown_viewer.show_table_of_contents = not markdown_viewer.show_table_of_contents

    app = MarkdownApp()
    app.run()


@main.command("print", section=EXAMINE)
@cloup.option(
    "--format",
    type=cloup.Choice(["rich", "text", "json"], case_sensitive=False),
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
            print_json(cl.to_json(), indent=JSON_INDENT)


@main.command("added", section=ADD)
@cloup.argument("entries", nargs=-1)
def added(entries: List[str]):
    """
    Add new entries to "Added" change type.

    ex.: changeloggh added "New feature" "New validation added".

    \b
    ENTRIES  List of entries.
    """
    add_entry(ChangeType.Added, entries)


@main.command("changed", section=ADD)
@cloup.argument("entries", nargs=-1)
def changed(entries: List[str]):
    """
    Add new entries to "Changed" change type.

    ex.: changeloggh changed "Size was changed" "Change auth method".

    \b
    ENTRIES  List of entries.
    """
    add_entry(ChangeType.Changed, entries)


@main.command("deprecated", section=ADD)
@cloup.argument("entries", nargs=-1)
def deprecated(entries: List[str]):
    """
    Add new entries to "Deprecated" change type.

    ex.: changeloggh deprecated "Option force" "Add method".

    \b
    ENTRIES  List of entries.
    """
    add_entry(ChangeType.Deprecated, entries)


@main.command("fixed", section=ADD)
@cloup.argument("entries", nargs=-1)
def fixed(entries: List[str]):
    """
    Add new entries to "Fixed" change type.

    ex.: changeloggh fixed "Error when loading" "Fix panel size".

    \b
    ENTRIES  List of entries.
    """
    add_entry(ChangeType.Fixed, entries)


@main.command("removed", section=ADD)
@cloup.argument("entries", nargs=-1)
def removed(entries: List[str]):
    """
    Add new entries to "Removed" change type.

    ex.: changeloggh removed "Remove unnecessary code" "Remove deprecated function".

    \b
    ENTRIES  List of entries.
    """
    add_entry(ChangeType.Removed, entries)


@main.command("security", section=ADD)
@cloup.argument("entries", nargs=-1)
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


@main.command("latest", section=EXAMINE)
def latest():
    """
    Print latest version.
    """
    path = Path(CHANGELOG_LOCK_PATH)
    if not path.exists():
        print(f'{CHANGELOG_LOCK_PATH} file does not exist. Use "init" command to initialize.')
        exit(1)
    cl = load_changelog()
    print(cl.latest())


@main.command("bump", section=RELEASE)
@cloup.argument(
    "rule", type=cloup.Choice(["major", "minor", "patch"], case_sensitive=False), nargs=1
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


@main.command("release", section=RELEASE)
@cloup.argument("version", nargs=1)
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


@main.command("import", section=START)
@cloup.option(
    "--force",
    is_flag=True,
    default=False,
    help='Force to override the "changelog.lock" file.',
    show_default=True,
)
def import_md(force: bool):
    """
    Import a markdown file.
    """

    if not force:
        path = Path(CHANGELOG_LOCK_PATH)
        if path.exists():
            print(f"{CHANGELOG_LOCK_PATH} file already exists. Use --force to override the file.")
            exit(1)

    cl = parse_changelog()
    cl.save()
    print_json(cl.to_json(), indent=JSON_INDENT)


if __name__ == "__main__":
    main()
