from unittest import TestCase

from changeloggh.changelog import Changelog


class TestApp(TestCase):
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
