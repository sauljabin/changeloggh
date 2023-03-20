import json

from jinja2 import Environment

from changeloggh.change_type import ChangeType
from changeloggh.url_utils import url_join
from changeloggh.version_utils import version_comparator, change_comparator

LIST_KEY = "list"

TYPE_KEY = "type"

CHANGES_KEY = "changes"

CHANGELOG_PATH = "./CHANGELOG.md"
CHANGELOG_LOCK_PATH = "./changelog.lock"

LINK_KEY = "link"

VERSION_KEY = "version"

REPOSITORY_KEY = "repository"

VERSIONS_KEY = "versions"

JINJA_TEMPLATE = """
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
{% for version in versions %}
## [{{version.version.capitalize()}}]{% if version.date %} - {{version.date}}{% endif %}
{% for change in version.changes %}
### {{change.type.capitalize()}}
{% for item in change.list %}
- {{item}}
{% endfor %}{% endfor %}{% endfor %}
{% for link in links %}[{{link.version.capitalize()}}]: {{link.link}}
{% endfor %}
"""


def parse_changelog():
    pass


def load_changelog():
    with open(CHANGELOG_LOCK_PATH, "r") as content:
        input_data = json.load(content)
    return Changelog(input_data)


def empty_changelog(repository=""):
    return Changelog(
        {
            "repository": repository,
            "versions": [
                {
                    "version": "Unreleased",
                }
            ],
        }
    )


class Changelog:
    def __init__(self, data):
        if not isinstance(data, dict):
            raise TypeError("Argument must be dictionary.")

        self.data = data

        if self.data.get(VERSIONS_KEY) is None:
            self.data[VERSIONS_KEY] = []

        if self.data.get(REPOSITORY_KEY) is None:
            self.data[REPOSITORY_KEY] = ""

        self.data[VERSIONS_KEY].sort(key=version_comparator())

        for version in self.data[VERSIONS_KEY]:
            if version.get(CHANGES_KEY) is not None:
                version[CHANGES_KEY].sort(key=change_comparator())

    def __str__(self):
        return self.to_string()

    def to_string(self):
        links = []
        versions = self.data[VERSIONS_KEY]
        repository = self.data[REPOSITORY_KEY]

        if len(versions) > 1 and repository:
            for index, version in enumerate(versions[:-1]):
                previous_tag = f"v{versions[index + 1][VERSION_KEY]}"
                current_tag = f"v{version[VERSION_KEY]}"

                if index == 0:
                    current_tag = "HEAD"

                links.append(
                    {
                        VERSION_KEY: version[VERSION_KEY],
                        LINK_KEY: url_join(
                            [repository, f"/compare/{previous_tag}...{current_tag}"]
                        ),
                    }
                )

            version = versions[-1][VERSION_KEY]
            links.append(
                {
                    VERSION_KEY: version,
                    LINK_KEY: url_join([repository, f"/releases/tag/v{version}"]),
                }
            )

        env = Environment()
        template = env.from_string(JINJA_TEMPLATE)
        return template.render(versions=versions, links=links).strip()

    def to_dict(self):
        return self.data

    def to_json(self, indent: int = None):
        return json.dumps(self.data, indent=indent)

    def save(self):
        with open(CHANGELOG_PATH, "w") as file:
            file.write(self.to_string())

        with open(CHANGELOG_LOCK_PATH, "w") as file:
            file.write(self.to_json(indent=4))

    def add(self, change_type: ChangeType, entry: str):
        unrelease_version = self.data[VERSIONS_KEY][0]

        if unrelease_version.get(CHANGES_KEY) is None:
            unrelease_version[CHANGES_KEY] = []
        changes = unrelease_version[CHANGES_KEY]

        for change in changes:
            inner_change_type = change.get(TYPE_KEY)
            if inner_change_type is not None and inner_change_type == change_type.value:
                if change.get(LIST_KEY) is None:
                    change[LIST_KEY] = []
                list = change[LIST_KEY]
                list.append(entry)
                break
        else:
            changes.append({TYPE_KEY: change_type.value, LIST_KEY: [entry]})

        changes.sort(key=change_comparator())


if __name__ == "__main__":
    data = {
        "repository": "https://github.com/sauljabin/changeloggh",
        "versions": [
            {
                "version": "Unreleased",
            },
            {
                "version": "0.0.1",
                "date": "2023-03-17",
                "changes": [
                    {
                        "type": "Added",
                        "list": [
                            "Initial setup",
                        ],
                    },
                ],
            },
        ],
    }
    cl = Changelog(data)
    print(cl.to_string())
    print(cl.to_dict())
    print(cl.to_json(indent=True))
