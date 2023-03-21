import json
from datetime import date
from enum import Enum
from typing import List, Any

from jinja2 import Environment
from semver import VersionInfo

from changeloggh.url_utils import url_join
from changeloggh.version_utils import version_comparator, change_comparator

CHANGELOG_PATH = "./CHANGELOG.md"
CHANGELOG_LOCK_PATH = "./changelog.lock"
JINJA_TEMPLATE = """
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
{% if versions %}{% for version in versions %}
## {{version}}
{% if version.changes %}{% for change in version.changes %}
### {{change}}
{% if change.entries %}{% for item in change.entries %}
- {{item}}{% endfor %}
{% endif %}{% endfor %}{% endif %}{% endfor %}{% endif %}
{% for link in links %}{{link}}
{% endfor %}
"""


class Link:
    def __init__(self, version: str = "", repository: str = "", path: str = ""):
        self.version = version
        self.repository = repository
        self.path = path

    def url(self):
        return url_join([self.repository, self.path])

    def __str__(self):
        return self.to_str()

    def to_str(self):
        return f"[{self.version.capitalize().strip()}]: {self.url()}"


class ChangeType(Enum):
    Added = "Added"
    Changed = "Changed"
    Deprecated = "Deprecated"
    Fixed = "Fixed"
    Removed = "Removed"
    Security = "Security"


class BumpRule(Enum):
    major = "major"
    minor = "minor"
    patch = "patch"


class Change:
    def __init__(self, change_type: str = "", entries: List[str] | None = None):
        self.change_type = change_type
        self.entries = entries

    def __eq__(self, other):
        return self.change_type == other.change_type

    def to_dict(self):
        change_dict = {}
        if self.change_type:
            change_dict["type"] = self.change_type
        if self.entries:
            change_dict["entries"] = self.entries
        return change_dict

    def __str__(self):
        return self.to_string()

    def to_string(self):
        if self.change_type:
            return f"{self.change_type.capitalize().strip()}"
        else:
            return None


class Version:
    def __init__(
        self,
        version: str = "",
        release_date: str | None = None,
        changes: List[Change] | None = None,
    ):
        self.release_date = release_date
        self.changes = changes
        self.version = version

        if self.changes:
            self.changes.sort(key=change_comparator())

    def __eq__(self, other):
        return self.version == other.version

    def to_dict(self):
        version_dict = {}
        if self.version:
            version_dict["version"] = self.version
        if self.release_date:
            version_dict["date"] = self.release_date
        if self.changes:
            version_dict["changes"] = [change.to_dict() for change in self.changes]
        return version_dict

    def __str__(self):
        return self.to_string()

    def to_string(self):
        if self.version:
            return (
                f"[{self.version.capitalize().strip()}] - {self.release_date}"
                if self.release_date
                else f"[{self.version.capitalize().strip()}]"
            )
        else:
            return None


class Changelog:
    def __init__(self, repository: str = "", versions: List[Version] | None = None):
        self.repository = repository
        self.versions = versions

        if self.versions:
            self.versions.sort(key=version_comparator())

    def __str__(self):
        return self.to_string()

    def to_string(self):
        links = []

        if self.versions and len(self.versions) > 1 and self.repository:
            for index, version in enumerate(self.versions[:-1]):
                previous_tag = f"v{self.versions[index + 1].version}"
                current_tag = f"v{version.version}"

                if index == 0:
                    current_tag = "HEAD"

                links.append(
                    Link(
                        version.version, self.repository, f"/compare/{previous_tag}...{current_tag}"
                    )
                )

            first_version = self.versions[-1]
            links.append(
                Link(
                    first_version.version,
                    self.repository,
                    f"/releases/tag/v{first_version.version}",
                )
            )

        env = Environment()
        template = env.from_string(JINJA_TEMPLATE)
        return template.render(versions=self.versions, links=links).strip()

    def to_json(self, indent: int = None):
        return json.dumps(self.to_dict(), indent=indent)

    def save(self):
        with open(CHANGELOG_PATH, "w") as file:
            file.write(self.to_string())

        with open(CHANGELOG_LOCK_PATH, "w") as file:
            file.write(self.to_json(indent=4))

    def add(self, change_type: ChangeType, entry: str):
        if self.versions is None:
            self.versions = []

        if len(self.versions) == 0 or (
            len(self.versions) == 1 and self.versions[0].version != "Unreleased"
        ):
            self.versions.append(Version("Unreleased"))
            self.versions.sort(key=version_comparator())

        unreleased_version = self.versions[0]

        if unreleased_version.changes is None:
            unreleased_version.changes = []

        for change in unreleased_version.changes:
            if change.change_type is not None and change.change_type == change_type.value:
                if change.entries is None:
                    change.entries = []
                change.entries.append(entry)
                break
        else:
            unreleased_version.changes.append(Change(change_type.value, [entry]))

        unreleased_version.changes.sort(key=change_comparator())

    def to_dict(self):
        changelog_dict = {}
        if self.repository:
            changelog_dict["repository"] = self.repository
        if self.versions:
            changelog_dict["versions"] = [version.to_dict() for version in self.versions]
        return changelog_dict

    def latest(self):
        if not self.versions or (
            len(self.versions) == 1 and self.versions[0].version == "Unreleased"
        ):
            return "0.0.0"

        if len(self.versions) == 1 and self.versions[0].version != "Unreleased":
            return self.versions[0].version

        return self.versions[1].version

    def bump(self, rule: BumpRule):
        if not self.versions:
            raise Exception("There are not available versions")

        if (
            not self.versions[0].changes
            or not self.versions[0].version
            or self.versions[0].version != "Unreleased"
        ):
            raise Exception("There are not available changes")

        semver = VersionInfo.parse(self.latest())

        match rule:
            case BumpRule.major:
                semver = semver.bump_major()
            case BumpRule.minor:
                semver = semver.bump_minor()
            case BumpRule.patch:
                semver = semver.bump_patch()

        self.versions.append(Version(str(semver), str(date.today()), self.versions[0].changes))
        self.versions[0].changes = None
        self.versions.sort(key=version_comparator())

        return str(semver)

    def release(self, version: str):
        if not self.versions:
            raise Exception("There are not available versions")

        if (
            not self.versions[0].changes
            or not self.versions[0].version
            or self.versions[0].version != "Unreleased"
        ):
            raise Exception("There are not available changes")

        for inner_version in self.versions:
            if inner_version.version == version:
                raise Exception(f"Version {version} exists already")

        semver = VersionInfo.parse(version)
        self.versions.append(Version(str(semver), str(date.today()), self.versions[0].changes))
        self.versions[0].changes = None
        self.versions.sort(key=version_comparator())
        return str(semver)


def load_changelog() -> Changelog:
    def json_to_changelog(obj: dict[Any, Any]):
        if "type" in obj:
            return Change(change_type=obj["type"], entries=obj.get("entries"))
        if "version" in obj:
            return Version(
                version=obj["version"], release_date=obj.get("date"), changes=obj.get("changes")
            )
        if "repository" in obj:
            return Changelog(repository=obj["repository"], versions=obj.get("versions"))
        return obj

    with open(CHANGELOG_LOCK_PATH, "r") as content:
        changelog = json.load(content, object_hook=json_to_changelog)

    return changelog


def empty_changelog(repository="") -> Changelog:
    return Changelog(repository=repository, versions=[Version(version="Unreleased")])


def parse_changelog() -> Changelog:
    with open(CHANGELOG_PATH, "r") as content:
        lines = content.readlines()

    versions = []
    repo = ""

    for line in lines:
        if line.startswith("## "):
            version_header = line.strip("##").strip().split(" - ")
            str_version = version_header[0].strip("[").strip("]")
            str_date = version_header[1] if len(version_header) > 1 else None
            versions.append(Version(version=str_version, release_date=str_date, changes=[]))
        if line.startswith("### "):
            version = versions[-1]
            version.changes.append(Change(change_type=line.strip("### ").strip(), entries=[]))
        if line.startswith("- "):
            version = versions[-1]
            change = version.changes[-1]
            change.entries.append(line.strip("- ").strip())
        if line.startswith("[Unreleased]: "):
            repo = line.strip().strip("[Unreleased]: ")
            repo = repo[: repo.index("/compare")]

    return Changelog(versions=versions, repository=repo)


if __name__ == "__main__":
    versions_test = [
        Version("Unreleased"),
        Version("0.0.1", "2023-03-17", [Change("Added", ["Initial setup"])]),
    ]

    cl = Changelog(repository="https://github.com/sauljabin/changeloggh", versions=versions_test)
    print(cl.to_string())
    print(cl.to_dict())
    print(cl.to_json(indent=True))
