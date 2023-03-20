from unittest import TestCase

from changeloggh.version_utils import version_comparator, change_comparator


class TestApp(TestCase):
    def test_sort_versions(self):
        data = [
            {"version": "0.0.1"},
            {"version": "Unreleased"},
            {"version": "1.0.4"},
            {"version": "2.3.0"},
            {"version": "1.5.0"},
            {"version": "1.3.0"},
        ]

        expected_data = [
            {"version": "Unreleased"},
            {"version": "2.3.0"},
            {"version": "1.5.0"},
            {"version": "1.3.0"},
            {"version": "1.0.4"},
            {"version": "0.0.1"},
        ]

        data.sort(key=version_comparator())

        self.assertEqual(expected_data, data)

    def test_sort_changes(self):
        data = [
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
        ]
        expected_data = [
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
        ]

        data.sort(key=change_comparator())

        self.assertEqual(expected_data, data)
