import copy
import json
from datetime import date
from unittest import TestCase
from unittest.mock import patch, mock_open, call

from changeloggh.changelog import (
    Change,
    Changelog,
    Version,
    empty_changelog,
    load_changelog,
    ChangeType,
    BumpRule,
    parse_changelog,
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

    def test_raise_error_if_there_are_not_versions(self):
        with self.assertRaises(Exception) as context:
            cl = Changelog(versions=[])
            cl.bump(BumpRule.patch)

        self.assertEqual("There are not available versions", str(context.exception))

    def test_raise_error_if_there_are_not_changes(self):
        with self.assertRaises(Exception) as context:
            cl = Changelog(versions=[Version("Unreleased")])
            cl.bump(BumpRule.patch)

        self.assertEqual("There are not available changes", str(context.exception))

    def test_raise_error_if_there_is_not_unreleased(self):
        with self.assertRaises(Exception) as context:
            cl = Changelog(versions=[Version("0.0.1", changes=[Change()])])
            cl.bump(BumpRule.patch)

        self.assertEqual("There are not available changes", str(context.exception))

    def test_raise_error_if_version_is_none(self):
        with self.assertRaises(Exception) as context:
            cl = Changelog(versions=[Version(changes=[Change()])])
            cl.bump(BumpRule.patch)

        self.assertEqual("There are not available changes", str(context.exception))

    def test_get_version_zero_if_no_versions(self):
        cl = Changelog(versions=[])
        self.assertEqual("0.0.0", cl.latest())

    def test_get_version_zero_if_there_is_only_unreleased(self):
        cl = Changelog(versions=[Version("Unreleased")])
        self.assertEqual("0.0.0", cl.latest())

    def test_get_version_if_there_is_only_one(self):
        version = "0.0.1"
        cl = Changelog(versions=[Version(version)])
        self.assertEqual(version, cl.latest())

    def test_get_version_happy_path(self):
        version = "0.0.1"
        cl = Changelog(versions=[Version("Unreleased"), Version(version)])
        self.assertEqual(version, cl.latest())

    def test_bump_version_whit_no_previous_version(self):
        for rule, version in [("patch", "0.0.1"), ("minor", "0.1.0"), ("major", "1.0.0")]:
            expected_data = {
                "versions": [
                    {
                        "version": "Unreleased",
                    },
                    {
                        "version": version,
                        "date": str(date.today()),
                        "changes": [
                            {"type": "Added", "entries": ["Initial"]},
                        ],
                    },
                ],
            }
            cl = Changelog(
                versions=[
                    Version(
                        version="Unreleased",
                        changes=[Change(change_type="Added", entries=["Initial"])],
                    )
                ]
            )

            cl.bump(BumpRule[rule])

            self.assertEqual(expected_data, cl.to_dict())

    def test_bump_version_whit_with_previous_version(self):
        for rule, version in [("patch", "1.0.1"), ("minor", "1.1.0"), ("major", "2.0.0")]:
            expected_data = {
                "versions": [
                    {
                        "version": "Unreleased",
                    },
                    {
                        "version": version,
                        "date": str(date.today()),
                        "changes": [
                            {"type": "Added", "entries": ["Test"]},
                        ],
                    },
                    {
                        "version": "1.0.0",
                        "date": str(date.today()),
                        "changes": [
                            {"type": "Added", "entries": ["Initial"]},
                        ],
                    },
                ],
            }
            cl = Changelog(
                versions=[
                    Version(
                        version="Unreleased",
                        changes=[Change(change_type="Added", entries=["Test"])],
                    ),
                    Version(
                        version="1.0.0",
                        release_date=str(date.today()),
                        changes=[Change(change_type="Added", entries=["Initial"])],
                    ),
                ]
            )

            cl.bump(BumpRule[rule])

            self.assertEqual(expected_data, cl.to_dict())

    def test_raise_error_if_there_are_not_versions_on_release(self):
        with self.assertRaises(Exception) as context:
            cl = Changelog(versions=[])
            cl.release("")

        self.assertEqual("There are not available versions", str(context.exception))

    def test_raise_error_if_there_are_not_changes_on_release(self):
        with self.assertRaises(Exception) as context:
            cl = Changelog(versions=[Version("Unreleased")])
            cl.release("")

        self.assertEqual("There are not available changes", str(context.exception))

    def test_raise_error_if_there_is_not_unreleased_on_release(self):
        with self.assertRaises(Exception) as context:
            cl = Changelog(versions=[Version("0.0.1", changes=[Change()])])
            cl.release("")

        self.assertEqual("There are not available changes", str(context.exception))

    def test_raise_error_if_version_is_none_on_release(self):
        with self.assertRaises(Exception) as context:
            cl = Changelog(versions=[Version(changes=[Change()])])
            cl.release("")

        self.assertEqual("There are not available changes", str(context.exception))

    def test_raise_error_if_version_is_not_allowed_release(self):
        with self.assertRaises(Exception) as context:
            cl = Changelog(
                versions=[
                    Version(
                        version="Unreleased",
                        changes=[Change(change_type="Added", entries=["Test"])],
                    ),
                ]
            )
            cl.release("random")

        self.assertEqual("random is not valid SemVer string", str(context.exception))

    def test_release_version_whit_with_previous_version(self):
        version = "2.1.3"
        expected_data = {
            "versions": [
                {
                    "version": "Unreleased",
                },
                {
                    "version": version,
                    "date": str(date.today()),
                    "changes": [
                        {"type": "Added", "entries": ["Test"]},
                    ],
                },
                {
                    "version": "1.0.0",
                    "date": str(date.today()),
                    "changes": [
                        {"type": "Added", "entries": ["Initial"]},
                    ],
                },
            ],
        }
        cl = Changelog(
            versions=[
                Version(
                    version="Unreleased",
                    changes=[Change(change_type="Added", entries=["Test"])],
                ),
                Version(
                    version="1.0.0",
                    release_date=str(date.today()),
                    changes=[Change(change_type="Added", entries=["Initial"])],
                ),
            ]
        )

        cl.release(version)

        self.assertEqual(expected_data, cl.to_dict())

    def test_raise_error_if_release_version_exists_already(self):
        version = "1.0.0"
        with self.assertRaises(Exception) as context:
            cl = Changelog(
                versions=[
                    Version(
                        version="Unreleased",
                        changes=[Change(change_type="Added", entries=["Test"])],
                    ),
                    Version(
                        version="1.0.0",
                        release_date=str(date.today()),
                        changes=[Change(change_type="Added", entries=["Initial"])],
                    ),
                ]
            )

            cl.release(version)

        self.assertEqual("Version 1.0.0 exists already", str(context.exception))

    @patch("builtins.open", new_callable=mock_open, read_data=CHANGELOG_EXAMPLE)
    def test_import(self, mock_open_function):
        cl = parse_changelog()
        self.assertEqual(DICT_EXAMPLE, cl.to_dict())
