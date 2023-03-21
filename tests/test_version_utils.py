from unittest import TestCase

from changeloggh.changelog import Version, Change
from changeloggh.version_utils import version_comparator, change_comparator


class TestApp(TestCase):
    def test_sort_versions(self):
        data = [
            Version("1.5.2"),
            Version("0.0.1"),
            Version("1.5.4"),
            Version("Unreleased"),
            Version("2.3.0"),
            Version("1.3.0"),
        ]

        expected_data = [
            Version("Unreleased"),
            Version("2.3.0"),
            Version("1.5.4"),
            Version("1.5.2"),
            Version("1.3.0"),
            Version("0.0.1"),
        ]

        data.sort(key=version_comparator())

        self.assertEqual(expected_data, data)

    def test_sort_changes(self):
        data = [
            Change("Fixed"),
            Change("Security"),
            Change("Deprecated"),
            Change("Removed"),
            Change("Added"),
            Change("Changed"),
        ]
        expected_data = [
            Change("Added"),
            Change("Changed"),
            Change("Deprecated"),
            Change("Fixed"),
            Change("Removed"),
            Change("Security"),
        ]

        data.sort(key=change_comparator())

        self.assertEqual(expected_data, data)
