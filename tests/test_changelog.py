import copy
import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, mock_open, call

from changeloggh.change_type import ChangeType
from changeloggh.changelog import Changelog, empty_changelog, load_changelog

REPO_INPUT = "https://github.com/sauljabin/changeloggh"

CHANGELOG_HEADER = """
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
""".strip()

CHANGELOG_EXAMPLE = f"""
{CHANGELOG_HEADER}

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

DATA_EXAMPLE = {
    "repository": REPO_INPUT,
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
                    "list": [
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
                    "list": [
                        "Initial setup",
                    ],
                },
            ],
        },
    ],
}

JSON_EXAMPLE = json.dumps(DATA_EXAMPLE)
JSON_INDENT_EXAMPLE = json.dumps(DATA_EXAMPLE, indent=4)


class TestApp(TestCase):
    def test_raise_error_if_not_dict(self):
        inputs = ["path", Path()]
        for invalid_input in inputs:
            with self.assertRaises(TypeError) as context:
                Changelog(invalid_input)

            self.assertIsInstance(context.exception, TypeError)
            self.assertEqual("Argument must be dictionary.", str(context.exception))

    def test_do_not_raise_error_if_input_is_dict(self):
        Changelog({})

    def test_string(self):
        dict_input = json.loads(JSON_EXAMPLE)
        cl = Changelog(dict_input)
        self.assertEqual(CHANGELOG_EXAMPLE, str(cl))
        self.assertEqual(CHANGELOG_EXAMPLE, cl.to_string())

    def test_string_only_header(self):
        cl = Changelog({})
        self.assertEqual(CHANGELOG_HEADER, str(cl))
        self.assertEqual(CHANGELOG_HEADER, cl.to_string())

    def test_json(self):
        dict_input = json.loads(JSON_EXAMPLE)
        cl = Changelog(dict_input)
        self.assertEqual(JSON_EXAMPLE, cl.to_json())

    def test_json_indent(self):
        dict_input = json.loads(JSON_EXAMPLE)
        cl = Changelog(dict_input)
        self.assertEqual(JSON_INDENT_EXAMPLE, cl.to_json(indent=4))

    def test_dict(self):
        dict_input = json.loads(JSON_EXAMPLE)
        cl = Changelog(dict_input)
        self.assertEqual(DATA_EXAMPLE, cl.to_dict())

    @patch("builtins.open", new_callable=mock_open)
    def test_save(self, mock_function_open):
        cl = Changelog(DATA_EXAMPLE)

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
                "repository": "",
                "versions": [
                    {
                        "version": "Unreleased",
                    }
                ],
            },
            cl.to_dict(),
        )

    def test_empty_changelog_with_repo(self):
        cl = empty_changelog(REPO_INPUT)
        self.assertEqual(
            {
                "repository": REPO_INPUT,
                "versions": [
                    {
                        "version": "Unreleased",
                    }
                ],
            },
            cl.to_dict(),
        )

    @patch("builtins.open", new_callable=mock_open, read_data=JSON_INDENT_EXAMPLE)
    @patch("changeloggh.changelog.json")
    def test_load_changelog(self, mock_json_package, mock_open_function):
        mock_json_package.load.return_value = DATA_EXAMPLE

        cl = load_changelog()

        mock_json_package.load.assert_called_once_with(mock_open_function.return_value)
        self.assertEqual(DATA_EXAMPLE, cl.to_dict())

    def test_add_change_added(self):
        cl = Changelog(copy.deepcopy(DATA_EXAMPLE))

        cl.add(ChangeType.Added, "new change 1")
        cl.add(ChangeType.Added, "new change 2")

        expected = {
            "version": "Unreleased",
            "changes": [
                {
                    "type": "Added",
                    "list": [
                        "new change 1",
                        "new change 2",
                    ],
                },
            ],
        }
        self.assertEqual(expected, cl.to_dict()["versions"][0])

    def test_add_and_sort_change_added(self):
        cl = Changelog(copy.deepcopy(DATA_EXAMPLE))

        cl.add(ChangeType.Security, "new security change 1")
        cl.add(ChangeType.Added, "new added change")
        cl.add(ChangeType.Security, "new security change 2")

        expected = {
            "version": "Unreleased",
            "changes": [
                {
                    "type": "Added",
                    "list": [
                        "new added change",
                    ],
                },
                {
                    "type": "Security",
                    "list": [
                        "new security change 1",
                        "new security change 2",
                    ],
                },
            ],
        }
        self.assertEqual(expected, cl.to_dict()["versions"][0])

    def test_sort_versions(self):
        input_data = {
            "repository": "",
            "versions": [
                {"version": "0.0.1"},
                {"version": "Unreleased"},
                {"version": "1.0.4"},
                {"version": "2.3.0"},
                {"version": "1.5.0"},
                {"version": "1.3.0"},
            ],
        }
        expected_data = {
            "repository": "",
            "versions": [
                {"version": "Unreleased"},
                {"version": "2.3.0"},
                {"version": "1.5.0"},
                {"version": "1.3.0"},
                {"version": "1.0.4"},
                {"version": "0.0.1"},
            ],
        }
        cl = Changelog(input_data)

        self.assertEqual(expected_data, cl.to_dict())

    def test_sort_changes(self):
        input_data = {
            "repository": "",
            "versions": [
                {
                    "version": "Unreleased",
                    "changes": [
                        {
                            "type": "Fixed",
                        },
                        {
                            "type": "Security",
                        },
                        {
                            "type": "Deprecated",
                        },
                        {
                            "type": "Removed",
                        },
                        {
                            "type": "Added",
                        },
                        {
                            "type": "Changed",
                        },
                    ],
                },
            ],
        }
        expected_data = {
            "repository": "",
            "versions": [
                {
                    "version": "Unreleased",
                    "changes": [
                        {"type": "Added", "list": ["test1"]},
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
        cl = Changelog(input_data)

        cl.add(ChangeType.Added, "test1")

        self.assertEqual(expected_data, cl.to_dict())

    def test_sort_changes_when_creating(self):
        input_data = {
            "repository": "",
            "versions": [
                {
                    "version": "Unreleased",
                    "changes": [
                        {
                            "type": "Fixed",
                        },
                        {
                            "type": "Security",
                        },
                        {
                            "type": "Deprecated",
                        },
                        {
                            "type": "Removed",
                        },
                        {
                            "type": "Added",
                        },
                        {
                            "type": "Changed",
                        },
                    ],
                },
            ],
        }
        expected_data = {
            "repository": "",
            "versions": [
                {
                    "version": "Unreleased",
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
        cl = Changelog(input_data)

        self.assertEqual(expected_data, cl.to_dict())
