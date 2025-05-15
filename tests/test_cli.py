"""Tests for cli.py."""

from unittest.mock import patch, MagicMock

import pytest

from git_fleet_manager.cli import main


@pytest.fixture
def mock_argparse():
    """Mock argparse for testing CLI."""
    with patch("git_fleet_manager.cli.argparse") as mock_argparse:
        mock_parser = MagicMock()
        mock_argparse.ArgumentParser.return_value = mock_parser
        mock_parser.parse_args.return_value = MagicMock()
        yield mock_argparse


class TestMain:
    """Tests for main function."""

    @patch("git_fleet_manager.cli.check_repositories_status")
    def test_main_status_command(self, mock_check_status, mock_argparse):
        """Test main function with status command."""
        # Setup
        args = MagicMock()
        args.command = "status"
        args.directory = "/test/dir"
        args.version = False
        mock_argparse.ArgumentParser().parse_args.return_value = args

        # Execute
        result = main()

        # Assert
        assert result == 0
        mock_check_status.assert_called_once_with("/test/dir")

    @patch("git_fleet_manager.cli.pull_repositories")
    def test_main_pull_command(self, mock_pull, mock_argparse):
        """Test main function with pull command."""
        # Setup
        args = MagicMock()
        args.command = "pull"
        args.directory = "/test/dir"
        args.version = False
        mock_argparse.ArgumentParser().parse_args.return_value = args

        # Execute
        result = main()

        # Assert
        assert result == 0
        mock_pull.assert_called_once_with("/test/dir")

    @patch("git_fleet_manager.cli.push_repositories")
    def test_main_push_command(self, mock_push, mock_argparse):
        """Test main function with push command."""
        # Setup
        args = MagicMock()
        args.command = "push"
        args.directory = "/test/dir"
        args.version = False
        mock_argparse.ArgumentParser().parse_args.return_value = args

        # Execute
        result = main()

        # Assert
        assert result == 0
        mock_push.assert_called_once_with("/test/dir")

    @patch("git_fleet_manager.cli.log_repositories")
    def test_main_log_command(self, mock_log, mock_argparse):
        """Test main function with log command."""
        # Setup
        args = MagicMock()
        args.command = "log"
        args.directory = "/test/dir"
        args.max_commits = 5
        args.version = False
        mock_argparse.ArgumentParser().parse_args.return_value = args

        # Execute
        result = main()

        # Assert
        assert result == 0
        mock_log.assert_called_once_with("/test/dir", 5)

    @patch("git_fleet_manager.__version__", "0.1.5")
    def test_main_version_flag(self, mock_argparse):
        """Test main function with --version flag."""
        # Setup
        args = MagicMock()
        args.command = None
        args.version = True
        mock_argparse.ArgumentParser().parse_args.return_value = args

        # Execute
        with patch("builtins.print") as mock_print:
            result = main()

            # Assert
            assert result == 0
            mock_print.assert_called_once_with("git-fleet-manager version 0.1.5")

    def test_main_unknown_command(self, mock_argparse):
        """Test main function with unknown command."""
        # Setup
        args = MagicMock()
        args.command = "unknown"
        args.version = False
        mock_argparse.ArgumentParser().parse_args.return_value = args

        # Execute
        with patch("builtins.print") as mock_print:
            result = main()

        # Assert
        assert result == 1
        mock_print.assert_any_call("Unknown command: unknown")
        mock_argparse.ArgumentParser().print_help.assert_called_once()
