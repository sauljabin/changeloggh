import json
from pathlib import Path
from unittest import TestCase

from changeloggh.changelog import Changelog

CHANGELOG_HEADER = """
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
""".strip()

CHANGELOG_EXAMPLE = f"""
{CHANGELOG_HEADER}

## [Unreleased]

## [0.0.1] - 2023-03-17

### Added

- Initial setup

[Unreleased]: https://github.com/sauljabin/changeloggh/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/sauljabin/changeloggh/releases/tag/v0.0.1
""".strip()


DATA_EXAMPLE = {
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

JSON_EXAMPLE = json.dumps(DATA_EXAMPLE)
JSON_INDENT_EXAMPLE = json.dumps(DATA_EXAMPLE, indent=True)


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
        self.assertEqual(JSON_INDENT_EXAMPLE, cl.to_json(indent=True))

    def test_dict(self):
        dict_input = json.loads(JSON_EXAMPLE)
        cl = Changelog(dict_input)
        self.assertEqual(DATA_EXAMPLE, cl.to_dict())
