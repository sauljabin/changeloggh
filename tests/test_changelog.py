import copy
import json
from unittest import TestCase
from unittest.mock import patch, mock_open, call

from changeloggh.changelog import (
    Change,
    Changelog,
    Version,
    empty_changelog,
    load_changelog,
    ChangeType,
)

REPO_EXAMPLE = "https://github.com/sauljabin/changeloggh"

CHANGELOG_HEADER_EXAMPLE = """
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
""".strip()

CHANGELOG_EXAMPLE = f"""
{CHANGELOG_HEADER_EXAMPLE}

## [Unreleased]

## [1.0.1] - 2023-03-17

### Added

- Tests

## [0.0.1] - 2023-03-17

### Added

- Initial setup

[Unreleased]: https://github.com/sauljabin/changeloggh/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/sauljabin/changeloggh/compare/v0.0.1...v1.0.1
[0.0.1]: https://github.com/sauljabin/changeloggh/releases/tag/v0.0.1
""".strip()

VERSIONS_EXAMPLE = [
    Version("Unreleased"),
    Version("1.0.1", "2023-03-17", [Change("Added", ["Tests"])]),
    Version("0.0.1", "2023-03-17", [Change("Added", ["Initial setup"])]),
]

DICT_EXAMPLE = {
    "repository": REPO_EXAMPLE,
    "versions": [
        {
            "version": "Unreleased",
        },
        {
            "version": "1.0.1",
            "date": "2023-03-17",
            "changes": [
                {
                    "type": "Added",
                    "entries": [
                        "Tests",
                    ],
                },
            ],
        },
        {
            "version": "0.0.1",
            "date": "2023-03-17",
            "changes": [
                {
                    "type": "Added",
                    "entries": [
                        "Initial setup",
                    ],
                },
            ],
        },
    ],
}

JSON_EXAMPLE = json.dumps(DICT_EXAMPLE)
JSON_INDENT_EXAMPLE = json.dumps(DICT_EXAMPLE, indent=4)


class TestApp(TestCase):
    maxDiff = None

    def test_string(self):
        cl = Changelog(repository=REPO_EXAMPLE, versions=VERSIONS_EXAMPLE)
        self.assertEqual(CHANGELOG_EXAMPLE, str(cl))
        self.assertEqual(CHANGELOG_EXAMPLE, cl.to_string())

    def test_string_only_header(self):
        cl = Changelog()
        self.assertEqual(CHANGELOG_HEADER_EXAMPLE, str(cl))
        self.assertEqual(CHANGELOG_HEADER_EXAMPLE, cl.to_string())

    def test_json(self):
        cl = Changelog(repository=REPO_EXAMPLE, versions=VERSIONS_EXAMPLE)
        self.assertEqual(JSON_EXAMPLE, cl.to_json())

    def test_json_indent(self):
        cl = Changelog(repository=REPO_EXAMPLE, versions=VERSIONS_EXAMPLE)
        self.assertEqual(JSON_INDENT_EXAMPLE, cl.to_json(indent=4))

    def test_dict(self):
        cl = Changelog(repository=REPO_EXAMPLE, versions=VERSIONS_EXAMPLE)
        self.assertEqual(DICT_EXAMPLE, cl.to_dict())

    @patch("builtins.open", new_callable=mock_open)
    def test_save(self, mock_function_open):
        cl = Changelog(repository=REPO_EXAMPLE, versions=VERSIONS_EXAMPLE)

        cl.save()

        mock_function_open.assert_has_calls(
            [call("./CHANGELOG.md", "w"), call("./changelog.lock", "w")], any_order=True
        )

        mock_function_open.return_value.write.assert_has_calls(
            [call(CHANGELOG_EXAMPLE), call(JSON_INDENT_EXAMPLE)]
        )

    def test_empty_changelog(self):
        cl = empty_changelog()
        self.assertEqual(
            {
                "versions": [
                    {
                        "version": "Unreleased",
                    }
                ],
            },
            cl.to_dict(),
        )

    def test_empty_changelog_with_repo(self):
        cl = empty_changelog(REPO_EXAMPLE)
        self.assertEqual(
            {
                "repository": REPO_EXAMPLE,
                "versions": [
                    {
                        "version": "Unreleased",
                    }
                ],
            },
            cl.to_dict(),
        )

    @patch("builtins.open", new_callable=mock_open, read_data=JSON_INDENT_EXAMPLE)
    def test_load_changelog(self, mock_open_function):
        cl = load_changelog()
        self.assertEqual(DICT_EXAMPLE, cl.to_dict())

    def test_add_change_added(self):
        cl = Changelog(versions=copy.deepcopy(VERSIONS_EXAMPLE))

        cl.add(ChangeType.Added, "new change 1")
        cl.add(ChangeType.Added, "new change 2")

        expected = {
            "version": "Unreleased",
            "changes": [
                {
                    "type": "Added",
                    "entries": [
                        "new change 1",
                        "new change 2",
                    ],
                },
            ],
        }
        self.assertEqual(expected, cl.to_dict()["versions"][0])

    def test_add_change_added_and_initialize_unreleased(self):
        cl = Changelog(repository=REPO_EXAMPLE, versions=[])

        cl.add(ChangeType.Added, "new change")

        expected = {
            "version": "Unreleased",
            "changes": [
                {
                    "type": "Added",
                    "entries": [
                        "new change",
                    ],
                },
            ],
        }
        self.assertEqual(expected, cl.to_dict()["versions"][0])

    def test_add_change_added_and_initialize_unreleased_if_another_exists(self):
        cl = Changelog(
            repository=REPO_EXAMPLE,
            versions=[Version("1.0.1", changes=[Change("Added", ["new change"])])],
        )

        cl.add(ChangeType.Added, "new change in unreleased")

        expected = [
            {
                "version": "Unreleased",
                "changes": [
                    {
                        "type": "Added",
                        "entries": [
                            "new change in unreleased",
                        ],
                    },
                ],
            },
            {
                "version": "1.0.1",
                "changes": [
                    {
                        "type": "Added",
                        "entries": [
                            "new change",
                        ],
                    },
                ],
            },
        ]
        self.assertEqual(expected, cl.to_dict()["versions"])

    def test_add_and_sort_change_added(self):
        cl = Changelog(versions=copy.deepcopy(VERSIONS_EXAMPLE))

        cl.add(ChangeType.Security, "new security change 1")
        cl.add(ChangeType.Added, "new added change")
        cl.add(ChangeType.Security, "new security change 2")

        expected = {
            "version": "Unreleased",
            "changes": [
                {
                    "type": "Added",
                    "entries": [
                        "new added change",
                    ],
                },
                {
                    "type": "Security",
                    "entries": [
                        "new security change 1",
                        "new security change 2",
                    ],
                },
            ],
        }
        self.assertEqual(expected, cl.to_dict()["versions"][0])

    def test_sort_versions(self):
        data = [
            Version("1.0.4"),
            Version("0.0.1"),
            Version("1.5.4"),
            Version("Unreleased"),
            Version("2.3.0"),
            Version("1.3.0"),
        ]

        expected_data = {
            "versions": [
                {"version": "Unreleased"},
                {"version": "2.3.0"},
                {"version": "1.5.4"},
                {"version": "1.3.0"},
                {"version": "1.0.4"},
                {"version": "0.0.1"},
            ],
        }
        cl = Changelog(versions=data)

        self.assertEqual(expected_data, cl.to_dict())

    def test_sort_changes(self):
        input_data = [
            Version(
                "Unreleased",
                changes=[
                    Change("Fixed"),
                    Change("Security"),
                    Change("Deprecated"),
                    Change("Removed"),
                    Change("Added"),
                    Change("Changed"),
                ],
            )
        ]
        expected_data = {
            "versions": [
                {
                    "version": "Unreleased",
                    "changes": [
                        {"type": "Added", "entries": ["test1"]},
                        {
                            "type": "Changed",
                        },
                        {
                            "type": "Deprecated",
                        },
                        {
                            "type": "Fixed",
                        },
                        {
                            "type": "Removed",
                        },
                        {
                            "type": "Security",
                        },
                    ],
                },
            ],
        }
        cl = Changelog(versions=input_data)

        cl.add(ChangeType.Added, "test1")

        self.assertEqual(expected_data, cl.to_dict())

    def test_sort_changes_when_creating(self):
        input_data = [
            Version(
                changes=[
                    Change("Fixed"),
                    Change("Security"),
                    Change("Deprecated"),
                    Change("Removed"),
                    Change("Added"),
                    Change("Changed"),
                ]
            )
        ]
        expected_data = {
            "versions": [
                {
                    "changes": [
                        {
                            "type": "Added",
                        },
                        {
                            "type": "Changed",
                        },
                        {
                            "type": "Deprecated",
                        },
                        {
                            "type": "Fixed",
                        },
                        {
                            "type": "Removed",
                        },
                        {
                            "type": "Security",
                        },
                    ],
                },
            ],
        }
        cl = Changelog(versions=input_data)

        self.assertEqual(expected_data, cl.to_dict())
