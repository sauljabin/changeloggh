from unittest import TestCase

from changeloggh.url_utils import url_join


class TestApp(TestCase):
    def test_add_segments(self):
        expected = "https://github.com/sauljabin/changeloggh/compare/v0.0.1...HEAD"

        self.assertEqual(
            expected,
            url_join(["https://github.com/sauljabin/changeloggh", "/compare/v0.0.1...HEAD"]),
        )
        self.assertEqual(
            expected,
            url_join(["https://github.com/sauljabin/changeloggh/", "compare/v0.0.1...HEAD"]),
        )
        self.assertEqual(
            expected,
            url_join(["https://github.com/sauljabin/changeloggh", "compare/v0.0.1...HEAD"]),
        )
        self.assertEqual(
            expected,
            url_join(["https://github.com/sauljabin/changeloggh/", "/compare/v0.0.1...HEAD"]),
        )
