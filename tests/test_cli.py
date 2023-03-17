from unittest import TestCase
from unittest.mock import patch, mock_open

from click.testing import CliRunner

from changeloggh import VERSION
from changeloggh.cli import main, CHANGELOG_TEMPLATE


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

        result = runner.invoke(main, ["init"])

        mock_class_path.assert_called_once_with("./CHANGELOG.md")
        self.assertEqual(1, result.exit_code)
        self.assertIn("./CHANGELOG.md file already exists", result.output)

    @patch("builtins.open", new_callable=mock_open)
    @patch("changeloggh.cli.Path")
    def test_init_changelog_file(self, mock_class_path, mock_function_open):
        runner = CliRunner()
        mock_class_path.return_value.exists.return_value = False

        result = runner.invoke(main, ["init"])

        mock_class_path.assert_called_once_with("./CHANGELOG.md")
        mock_function_open.assert_called_with(mock_class_path.return_value, "w")
        mock_function_open.return_value.write.assert_called_once_with(CHANGELOG_TEMPLATE)
        self.assertEqual(0, result.exit_code)

    @patch("builtins.open", new_callable=mock_open)
    @patch("changeloggh.cli.Path")
    def test_force_init_changelog_file(self, mock_class_path, mock_function_open):
        runner = CliRunner()
        mock_class_path.return_value.exists.return_value = True

        result = runner.invoke(main, ["init", "--force"])

        mock_class_path.assert_called_once_with("./CHANGELOG.md")
        mock_function_open.assert_called_with(mock_class_path.return_value, "w")
        mock_function_open.return_value.write.assert_called_once_with(CHANGELOG_TEMPLATE)
        self.assertEqual(0, result.exit_code)
