from unittest import TestCase
from unittest.mock import patch, call, MagicMock

from click.testing import CliRunner

from changeloggh import VERSION
from changeloggh.changelog import Changelog, ChangeType, BumpRule, Version, Change
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

    @patch("changeloggh.cli.load_changelog", new_callable=MagicMock())
    @patch("changeloggh.cli.Path")
    def test_add_changes_file(self, mock_class_path, mock_function_load):
        for change in ["added", "changed", "deprecated", "fixed", "removed", "security"]:
            mock_class_path.return_value.exists.return_value = True
            mock_function_load.return_value = MagicMock()

            feature1 = "feature 1"
            feature2 = "feature 2"
            runner = CliRunner()
            result = runner.invoke(main, [change, feature1, feature2])

            mock_function_load.assert_called()
            mock_function_load.return_value.add.assert_has_calls(
                [
                    call(ChangeType[change.capitalize()], feature1),
                    call(ChangeType[change.capitalize()], feature2),
                ]
            )
            mock_function_load.return_value.save.assert_called_once()
            self.assertEqual(0, result.exit_code)

    @patch("changeloggh.cli.Path")
    def test_reject_add_changes_if_file_does_not_exist(self, mock_class_path):
        for change in ["added", "changed", "deprecated", "fixed", "removed", "security"]:
            mock_class_path.return_value.exists.return_value = False

            runner = CliRunner()
            result = runner.invoke(main, [change, "test"])

            mock_class_path.assert_has_calls([call("./changelog.lock"), call().exists()])
            self.assertEqual(1, result.exit_code)
            self.assertEqual(
                './changelog.lock file does not exist. Use "init" command to initialize.',
                result.output.strip(),
            )

    @patch("changeloggh.cli.load_changelog")
    def test_latest(self, mock_function_load):
        cl = Changelog(repository=REPO_EXAMPLE, versions=VERSIONS_EXAMPLE)
        mock_function_load.return_value = cl

        runner = CliRunner()
        result = runner.invoke(main, ["latest"])

        self.assertEqual(0, result.exit_code)
        self.assertEqual("1.0.1", result.output.strip())

    @patch("changeloggh.cli.load_changelog")
    def test_bump_command(self, mock_function_load):
        for rule, version in [("major", "2.0.0"), ("minor", "1.1.0"), ("patch", "1.0.2")]:
            mock_function_load.return_value = MagicMock()
            mock_function_load.return_value.bump.return_value = version

            runner = CliRunner()
            result = runner.invoke(main, ["bump", rule])

            mock_function_load.assert_called()
            mock_function_load.return_value.bump.assert_called_with(BumpRule[rule])
            mock_function_load.return_value.save.assert_called_once()

            self.assertEqual(0, result.exit_code)
            self.assertEqual(version, result.output.strip())

    @patch("changeloggh.cli.load_changelog")
    def test_raise_error_in_bump_command_when_cl_is_empty(self, mock_function_load):
        rule = "major"
        mock_function_load.return_value = Changelog()

        runner = CliRunner()
        result = runner.invoke(main, ["bump", rule])

        mock_function_load.assert_called()
        self.assertEqual(1, result.exit_code)
        self.assertEqual(
            (
                "There are not available versions. Use"
                " {added|changed|deprecated|removed|fixed|security} commands to add changes."
            ),
            result.output.strip(),
        )

    @patch("changeloggh.cli.load_changelog")
    def test_release_command(self, mock_function_load):
        version = "1.0.2"
        mock_function_load.return_value = MagicMock()
        mock_function_load.return_value.release.return_value = version

        runner = CliRunner()
        result = runner.invoke(main, ["release", version])

        mock_function_load.assert_called()
        mock_function_load.return_value.release.assert_called_with(version)
        mock_function_load.return_value.save.assert_called_once()

        self.assertEqual(0, result.exit_code)
        self.assertEqual(version, result.output.strip())

    @patch("changeloggh.cli.load_changelog")
    def test_raise_error_in_release_command_when_cl_is_empty(self, mock_function_load):
        version = "1.0.1"
        mock_function_load.return_value = Changelog()

        runner = CliRunner()
        result = runner.invoke(main, ["release", version])

        mock_function_load.assert_called()
        self.assertEqual(1, result.exit_code)
        self.assertEqual(
            (
                "There are not available versions. Use"
                " {added|changed|deprecated|removed|fixed|security} commands to add changes."
            ),
            result.output.strip(),
        )

    @patch("changeloggh.cli.load_changelog")
    def test_raise_error_in_release_command_when_version_is_invalid(self, mock_function_load):
        version = "random"
        mock_function_load.return_value = Changelog(
            versions=[
                Version(
                    version="Unreleased",
                    changes=[Change(change_type="Added", entries=["Initial"])],
                )
            ]
        )

        runner = CliRunner()
        result = runner.invoke(main, ["release", version])

        mock_function_load.assert_called()
        self.assertEqual(1, result.exit_code)
        self.assertEqual(
            (
                "random is not valid SemVer string. Use"
                " {added|changed|deprecated|removed|fixed|security} commands to add changes."
            ),
            result.output.strip(),
        )
