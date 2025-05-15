"""Tests for git_utils.py."""

import subprocess
from unittest.mock import patch, MagicMock

import pytest

from git_fleet_manager.git_utils import (
    is_git_repo,
    get_repo_status,
    find_git_repositories,
    pull_repository,
)


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing git commands."""
    with patch("git_fleet_manager.git_utils.subprocess") as mock_subprocess:
        # Setup the CalledProcessError to have the correct class inheritance
        mock_subprocess.CalledProcessError = subprocess.CalledProcessError
        yield mock_subprocess


class TestIsgfmepo:
    """Tests for is_git_repo function."""

    def test_is_git_repo_true(self, mock_subprocess):
        """Test is_git_repo returns True for valid git repo."""
        # Setup
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_subprocess.run.return_value = mock_process

        # Execute
        result = is_git_repo("/path/to/repo")

        # Assert
        assert result is True
        mock_subprocess.run.assert_called_once()

    def test_is_git_repo_false(self, mock_subprocess):
        """Test is_git_repo returns False for non-git repo."""
        # Setup
        # Create a real CalledProcessError instance
        mock_subprocess.run.side_effect = subprocess.CalledProcessError(128, "git")

        # Execute
        result = is_git_repo("/path/to/non_repo")

        # Assert
        assert result is False
        mock_subprocess.run.assert_called_once()


class TestGetRepoStatus:
    """Tests for get_repo_status function."""

    @patch("git_fleet_manager.git_utils.is_git_repo")
    def test_get_repo_status_not_git_repo(self, mock_is_git_repo, mock_subprocess):
        """Test get_repo_status returns None for non-git repo."""
        # Setup
        mock_is_git_repo.return_value = False

        # Execute
        result = get_repo_status("/path/to/non_repo")

        # Assert
        assert result is None
        mock_is_git_repo.assert_called_once_with("/path/to/non_repo")

    @patch("git_fleet_manager.git_utils.is_git_repo")
    def test_get_repo_status_success(self, mock_is_git_repo, mock_subprocess):
        """Test get_repo_status returns correct status for git repo."""
        # Setup
        mock_is_git_repo.return_value = True

        branch_process = MagicMock()
        branch_process.stdout = "main\n"
        branch_process.returncode = 0

        status_process = MagicMock()
        # The actual implementation strips the output, so we need to account for that
        status_process.stdout = "M file.txt\n"  # The space gets stripped by .strip()
        status_process.returncode = 0

        unpushed_process = MagicMock()
        unpushed_process.stdout = "abc123 Commit message\n"
        unpushed_process.returncode = 0

        mock_subprocess.run.side_effect = [branch_process, status_process, unpushed_process]

        # Execute
        result = get_repo_status("/path/to/repo")

        # Assert
        assert result == {
            "branch": "main",
            "has_changes": True,
            "status": "M file.txt",  # This is what we get after strip()
            "has_unpushed": True,
            "unpushed": "abc123 Commit message",
        }
        assert mock_subprocess.run.call_count == 3


class TestPullRepository:
    """Tests for pull_repository function."""

    @patch("git_fleet_manager.git_utils.is_git_repo")
    def test_pull_repository_not_git_repo(self, mock_is_git_repo, mock_subprocess):
        """Test pull_repository handles non-git repo."""
        # Setup
        mock_is_git_repo.return_value = False

        # Execute
        result = pull_repository("/path/to/non_repo")

        # Assert
        assert result == {"status": "not_a_repo"}
        mock_is_git_repo.assert_called_once_with("/path/to/non_repo")

    @patch("git_fleet_manager.git_utils.get_repo_status")
    @patch("git_fleet_manager.git_utils.is_git_repo")
    def test_pull_repository_with_local_changes(self, mock_is_git_repo, mock_get_repo_status, mock_subprocess):
        """Test pull_repository handles repo with local changes."""
        # Setup
        mock_is_git_repo.return_value = True
        mock_get_repo_status.return_value = {"has_changes": True}

        # Execute
        result = pull_repository("/path/to/repo_with_changes")

        # Assert
        assert result == {"status": "local_changes"}
        mock_is_git_repo.assert_called_once_with("/path/to/repo_with_changes")
        mock_get_repo_status.assert_called_once_with("/path/to/repo_with_changes")

    @patch("git_fleet_manager.git_utils.get_repo_status")
    @patch("git_fleet_manager.git_utils.is_git_repo")
    def test_pull_repository_success(self, mock_is_git_repo, mock_get_repo_status, mock_subprocess):
        """Test pull_repository successfully pulls changes."""
        # Setup
        mock_is_git_repo.return_value = True
        mock_get_repo_status.return_value = {"has_changes": False}
        mock_subprocess.run.return_value = MagicMock(returncode=0)

        # Execute
        result = pull_repository("/path/to/clean_repo")

        # Assert
        assert result == {"status": "success"}
        mock_subprocess.run.assert_called_once()


@patch("git_fleet_manager.git_utils.Path")
@patch("git_fleet_manager.git_utils.os.walk")
class TestFindgfmepositories:
    """Tests for find_git_repositories function."""

    def test_find_git_repositories_with_gfm_file(self, mock_walk, mock_path):
        """Test find_git_repositories uses .gfm file when present."""
        # Setup mock Path
        mock_base_path = MagicMock()
        mock_base_path.exists.return_value = True
        mock_base_path.expanduser.return_value = mock_base_path
        mock_base_path.resolve.return_value = mock_base_path

        mock_gfm_file = MagicMock()
        mock_gfm_file.exists.return_value = True
        mock_base_path.__truediv__.return_value = mock_gfm_file

        mock_path.return_value = mock_base_path

        # Mock reading .gfm file
        mock_file = MagicMock()
        mock_file.__enter__.return_value = ["repo1\n", "repo2\n"]
        mock_gfm_file.open.return_value = mock_file

        # Mock repo paths from .gfm
        mock_repo1 = MagicMock()
        mock_repo1.exists.return_value = True
        mock_repo1.name = "repo1"

        mock_repo2 = MagicMock()
        mock_repo2.exists.return_value = True
        mock_repo2.name = "repo2"

        mock_base_path.__truediv__.side_effect = [mock_gfm_file, mock_repo1, mock_repo2]

        # Setup mock is_git_repo
        with patch("git_fleet_manager.git_utils.is_git_repo") as mock_is_git_repo:
            mock_is_git_repo.return_value = True

            # Execute
            result = find_git_repositories("/path/to/base")

            # Assert
            assert len(result) == 2
            assert mock_repo1 in result
            assert mock_repo2 in result
            mock_is_git_repo.assert_any_call(mock_repo1)
            mock_is_git_repo.assert_any_call(mock_repo2)
