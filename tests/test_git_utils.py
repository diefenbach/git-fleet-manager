"""Tests for git_utils.py."""

import subprocess
from unittest.mock import patch, MagicMock

import pytest

from git_fleet_manager.git_utils import (
    is_git_repo,
    get_repo_status,
    find_git_repositories,
    pull_repository,
    checkout_repository,
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


class TestCheckoutRepository:
    """Tests for checkout_repository function."""

    @patch("git_fleet_manager.git_utils.is_git_repo")
    def test_checkout_repository_not_git_repo(self, mock_is_git_repo, mock_subprocess):
        """Test checkout_repository handles non-git repo."""
        # Setup
        mock_is_git_repo.return_value = False

        # Execute
        result = checkout_repository("/path/to/non_repo", "main")

        # Assert
        assert result == {"status": "not_a_repo"}
        mock_is_git_repo.assert_called_once_with("/path/to/non_repo")

    @patch("git_fleet_manager.git_utils.is_git_repo")
    def test_checkout_repository_branch_not_found(self, mock_is_git_repo, mock_subprocess):
        """Test checkout_repository handles branch not found."""
        # Setup
        mock_is_git_repo.return_value = True

        # Mock local branch check (returns empty)
        local_branch_process = MagicMock()
        local_branch_process.stdout = ""
        local_branch_process.returncode = 0

        # Mock remote branch check (returns empty)
        remote_branch_process = MagicMock()
        remote_branch_process.stdout = ""
        remote_branch_process.returncode = 0

        mock_subprocess.run.side_effect = [local_branch_process, remote_branch_process]

        # Execute
        result = checkout_repository("/path/to/repo", "nonexistent-branch")

        # Assert
        assert result == {"status": "branch_not_found"}
        assert mock_subprocess.run.call_count == 2
        mock_is_git_repo.assert_called_once_with("/path/to/repo")

    @patch("git_fleet_manager.git_utils.is_git_repo")
    def test_checkout_repository_success_local_branch(self, mock_is_git_repo, mock_subprocess):
        """Test checkout_repository successfully checks out existing local branch."""
        # Setup
        mock_is_git_repo.return_value = True

        # Mock local branch check (returns branch)
        local_branch_process = MagicMock()
        local_branch_process.stdout = "  main"
        local_branch_process.returncode = 0

        # Mock remote branch check (returns empty)
        remote_branch_process = MagicMock()
        remote_branch_process.stdout = ""
        remote_branch_process.returncode = 0

        # Mock successful checkout
        checkout_process = MagicMock()
        checkout_process.returncode = 0

        mock_subprocess.run.side_effect = [local_branch_process, remote_branch_process, checkout_process]

        # Execute
        result = checkout_repository("/path/to/repo", "main")

        # Assert
        assert result == {"status": "success"}
        assert mock_subprocess.run.call_count == 3
        mock_is_git_repo.assert_called_once_with("/path/to/repo")

    @patch("git_fleet_manager.git_utils.is_git_repo")
    def test_checkout_repository_success_remote_branch(self, mock_is_git_repo, mock_subprocess):
        """Test checkout_repository successfully checks out existing remote branch."""
        # Setup
        mock_is_git_repo.return_value = True

        # Mock local branch check (returns empty)
        local_branch_process = MagicMock()
        local_branch_process.stdout = ""
        local_branch_process.returncode = 0

        # Mock remote branch check (returns remote branch)
        remote_branch_process = MagicMock()
        remote_branch_process.stdout = "  origin/feature-branch"
        remote_branch_process.returncode = 0

        # Mock successful checkout
        checkout_process = MagicMock()
        checkout_process.returncode = 0

        mock_subprocess.run.side_effect = [local_branch_process, remote_branch_process, checkout_process]

        # Execute
        result = checkout_repository("/path/to/repo", "feature-branch")

        # Assert
        assert result == {"status": "success"}
        assert mock_subprocess.run.call_count == 3
        mock_is_git_repo.assert_called_once_with("/path/to/repo")

    @patch("git_fleet_manager.git_utils.is_git_repo")
    def test_checkout_repository_checkout_failed(self, mock_is_git_repo, mock_subprocess):
        """Test checkout_repository handles checkout failure."""
        # Setup
        mock_is_git_repo.return_value = True

        # Mock local branch check (returns branch)
        local_branch_process = MagicMock()
        local_branch_process.stdout = "  main"
        local_branch_process.returncode = 0

        # Mock remote branch check (returns empty)
        remote_branch_process = MagicMock()
        remote_branch_process.stdout = ""
        remote_branch_process.returncode = 0

        # Mock failed checkout
        mock_subprocess.run.side_effect = [
            local_branch_process,
            remote_branch_process,
            subprocess.CalledProcessError(1, "git checkout"),
        ]

        # Execute
        result = checkout_repository("/path/to/repo", "main")

        # Assert
        assert result == {"status": "checkout_failed"}
        assert mock_subprocess.run.call_count == 3
        mock_is_git_repo.assert_called_once_with("/path/to/repo")


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


class TestCheckoutRepositories:
    """Tests for checkout_repositories bulk function."""

    @patch("builtins.print")
    def test_checkout_repositories_no_branch_name(self, mock_print):
        """Test checkout_repositories handles missing branch name."""
        from git_fleet_manager.git_utils import checkout_repositories

        # Execute
        checkout_repositories("/test/dir", None)

        # Assert
        mock_print.assert_called_with("Error: branch_name is required for checkout operation")

    @patch("builtins.print")
    @patch("git_fleet_manager.git_utils.find_git_repositories")
    def test_checkout_repositories_no_repos_found(self, mock_find_repos, mock_print):
        """Test checkout_repositories handles no repositories found."""
        from git_fleet_manager.git_utils import checkout_repositories

        # Setup
        mock_find_repos.return_value = []

        # Execute
        checkout_repositories("/test/dir", "main")

        # Assert
        mock_find_repos.assert_called_once_with("/test/dir")
        mock_print.assert_called_with("No git repositories found in /test/dir")

    @patch("sys.stdout")
    @patch("builtins.print")
    @patch("git_fleet_manager.git_utils.checkout_repository")
    @patch("git_fleet_manager.git_utils.find_git_repositories")
    def test_checkout_repositories_success(self, mock_find_repos, mock_checkout_repo, mock_print, mock_stdout):
        """Test checkout_repositories successfully processes multiple repositories."""
        from git_fleet_manager.git_utils import checkout_repositories

        # Setup
        mock_repo1 = MagicMock()
        mock_repo1.name = "repo1"
        mock_repo2 = MagicMock()
        mock_repo2.name = "repo2"
        mock_find_repos.return_value = [mock_repo1, mock_repo2]

        mock_checkout_repo.side_effect = [{"status": "success"}, {"status": "branch_not_found"}]

        # Execute
        checkout_repositories("/test/dir", "develop")

        # Assert
        mock_find_repos.assert_called_once_with("/test/dir")
        assert mock_checkout_repo.call_count == 2
        mock_checkout_repo.assert_any_call(mock_repo1, "develop")
        mock_checkout_repo.assert_any_call(mock_repo2, "develop")

        # Check that print was called for headers and status messages
        assert mock_print.call_count >= 3  # At least header + separators + status messages

    @patch("sys.stdout")
    @patch("builtins.print")
    @patch("git_fleet_manager.git_utils.checkout_repository")
    @patch("git_fleet_manager.git_utils.find_git_repositories")
    def test_checkout_repositories_mixed_results(self, mock_find_repos, mock_checkout_repo, mock_print, mock_stdout):
        """Test checkout_repositories handles mixed results correctly."""
        from git_fleet_manager.git_utils import checkout_repositories

        # Setup
        mock_repo1 = MagicMock()
        mock_repo1.name = "repo1"
        mock_repo2 = MagicMock()
        mock_repo2.name = "repo2"
        mock_repo3 = MagicMock()
        mock_repo3.name = "repo3"
        mock_repo4 = MagicMock()
        mock_repo4.name = "repo4"
        mock_find_repos.return_value = [mock_repo1, mock_repo2, mock_repo3, mock_repo4]

        mock_checkout_repo.side_effect = [
            {"status": "success"},
            {"status": "branch_not_found"},
            {"status": "checkout_failed"},
            {"status": "not_a_repo"},
        ]

        # Execute
        checkout_repositories("/test/dir", "feature")

        # Assert
        mock_find_repos.assert_called_once_with("/test/dir")
        assert mock_checkout_repo.call_count == 4

        # Check that print was called for the different status messages
        # We know the function calls print for header, progress, and status messages
        assert mock_print.call_count >= 4  # At least header + separators + status messages

        # Check that the checkout_repository function was called with correct arguments
        expected_calls = [
            (mock_repo1, "feature"),
            (mock_repo2, "feature"),
            (mock_repo3, "feature"),
            (mock_repo4, "feature"),
        ]
        actual_calls = [(call[0][0], call[0][1]) for call in mock_checkout_repo.call_args_list]
        for expected_call in expected_calls:
            assert expected_call in actual_calls

    @patch("sys.stdout")
    @patch("builtins.print")
    @patch("git_fleet_manager.git_utils.checkout_repository")
    @patch("git_fleet_manager.git_utils.find_git_repositories")
    def test_checkout_repositories_with_exception(self, mock_find_repos, mock_checkout_repo, mock_print, mock_stdout):
        """Test checkout_repositories handles exceptions during checkout."""
        from git_fleet_manager.git_utils import checkout_repositories

        # Setup
        mock_repo1 = MagicMock()
        mock_repo1.name = "repo1"
        mock_find_repos.return_value = [mock_repo1]

        # Mock an exception being raised
        mock_checkout_repo.side_effect = Exception("Test exception")

        # Execute
        checkout_repositories("/test/dir", "main")

        # Assert
        mock_find_repos.assert_called_once_with("/test/dir")
        mock_checkout_repo.assert_called_once_with(mock_repo1, "main")

        # Check that error is handled and printed
        assert mock_print.call_count >= 3  # At least header + separators + error message
