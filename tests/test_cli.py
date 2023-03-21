from unittest import TestCase
from unittest.mock import patch, call, MagicMock

from click.testing import CliRunner

from changeloggh import VERSION
from changeloggh.changelog import Changelog
from changeloggh.cli import main
from tests.test_changelog import (
    REPO_EXAMPLE,
    CHANGELOG_EXAMPLE,
    JSON_INDENT_EXAMPLE,
    VERSIONS_EXAMPLE,
)


class TestApp(TestCase):
    def test_print_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(VERSION, result.output)

    @patch("changeloggh.cli.Path")
    def test_reject_init_if_file_already_exists(self, mock_class_path):
        runner = CliRunner()
        mock_class_path.return_value.exists.return_value = True

        result = runner.invoke(main, ["init", REPO_EXAMPLE])

        mock_class_path.assert_has_calls([call("./CHANGELOG.md"), call().exists()])
        # , call("./changelog.lock"), call().exists()
        self.assertEqual(1, result.exit_code)
        self.assertEqual(
            "./CHANGELOG.md file already exists. Use --force to override the file.",
            result.output.strip(),
        )

    @patch("changeloggh.cli.Path")
    def test_reject_init_if_lock_file_already_exists(self, mock_class_path):
        runner = CliRunner()
        mock_class_path.return_value.exists.side_effect = [False, True]

        result = runner.invoke(main, ["init", REPO_EXAMPLE])

        mock_class_path.assert_has_calls(
            [call("./CHANGELOG.md"), call().exists(), call("./changelog.lock"), call().exists()]
        )
        self.assertEqual(1, result.exit_code)
        self.assertEqual(
            "./changelog.lock file already exists. Use --force to override the file.",
            result.output.strip(),
        )

    @patch("changeloggh.cli.empty_changelog")
    @patch("changeloggh.cli.Path")
    def test_init_changelog_file(self, mock_class_path, mock_function_empty):
        mock_class_path.return_value.exists.side_effect = [False, False]

        runner = CliRunner()
        result = runner.invoke(main, ["init", REPO_EXAMPLE])

        mock_function_empty.assert_called_with(REPO_EXAMPLE)
        mock_function_empty.return_value.save.assert_called_once()
        self.assertEqual(0, result.exit_code)

    @patch("changeloggh.cli.empty_changelog")
    def test_force_init_changelog_file(self, mock_function_empty):
        mock_function_empty.return_value = MagicMock()

        runner = CliRunner()
        result = runner.invoke(main, ["init", "--force", REPO_EXAMPLE])

        mock_function_empty.assert_called_with(REPO_EXAMPLE)
        mock_function_empty.return_value.save.assert_called_once()
        self.assertEqual(0, result.exit_code)

    @patch("changeloggh.cli.load_changelog")
    def test_print_text(self, mock_function_load):
        mock_function_load.return_value = Changelog(
            repository=REPO_EXAMPLE, versions=VERSIONS_EXAMPLE
        )

        runner = CliRunner()
        result = runner.invoke(main, ["print", "--format", "text"])

        self.assertEqual(0, result.exit_code)
        self.assertEqual(CHANGELOG_EXAMPLE, result.output.strip())

    @patch("changeloggh.cli.load_changelog")
    def test_print_json(self, mock_function_load):
        mock_function_load.return_value = Changelog(
            repository=REPO_EXAMPLE, versions=VERSIONS_EXAMPLE
        )

        runner = CliRunner()
        result = runner.invoke(main, ["print", "--format", "json"])

        self.assertEqual(0, result.exit_code)
        self.assertEqual(JSON_INDENT_EXAMPLE, result.output.strip())

    @patch("changeloggh.cli.Markdown")
    @patch("changeloggh.cli.Console")
    @patch("changeloggh.cli.load_changelog")
    def test_print_default(self, mock_function_load, mock_console_function, mock_md_class):
        cl = Changelog(repository=REPO_EXAMPLE, versions=VERSIONS_EXAMPLE)
        mock_function_load.return_value = cl

        runner = CliRunner()
        result = runner.invoke(main, ["print"])

        mock_md_class.assert_called_once_with(cl.to_string())
        mock_console_function.return_value.print.assert_called_once_with(mock_md_class.return_value)
        self.assertEqual(0, result.exit_code)
