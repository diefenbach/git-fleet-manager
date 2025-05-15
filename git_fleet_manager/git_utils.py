"""
Utility functions for Git operations
"""

import os
import subprocess
import sys
from pathlib import Path
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

# Find the absolute path to the git executable
GIT_EXECUTABLE = shutil.which("git")
if GIT_EXECUTABLE is None:
    raise RuntimeError("git executable not found in PATH")


def is_git_repo(path):
    """Check if the given path is a git repository."""
    try:
        subprocess.run(
            [GIT_EXECUTABLE, "rev-parse", "--is-inside-work-tree"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_repo_status(path):
    """Get the status of a git repository."""
    if not is_git_repo(path):
        return None

    try:
        # Get current branch
        branch_process = subprocess.run(
            [GIT_EXECUTABLE, "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        branch = branch_process.stdout.strip()

        # Get status (changed files)
        status_process = subprocess.run(
            [GIT_EXECUTABLE, "status", "-s"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        status = status_process.stdout.strip()

        # Get unpushed commits
        unpushed_process = subprocess.run(
            [GIT_EXECUTABLE, "log", "@{u}..", "--oneline"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        unpushed = unpushed_process.stdout.strip() if unpushed_process.returncode == 0 else ""

        return {
            "branch": branch,
            "has_changes": bool(status),
            "status": status,
            "has_unpushed": bool(unpushed),
            "unpushed": unpushed,
        }
    except subprocess.CalledProcessError:
        return {"error": "Error getting repository status"}


def find_git_repositories(base_path):
    """Find all git repositories in the given base path and its subdirectories."""
    base_path = Path(base_path).expanduser().resolve()

    if not base_path.exists():
        print(f"Path does not exist: {base_path}")
        return []

    gfm_file = base_path / ".gfm"
    repositories = []

    if gfm_file.exists():
        # Use only repositories listed in the .gfm file
        with gfm_file.open("r") as file:
            for line in file:
                repo_path = base_path / line.strip()
                if repo_path.exists() and is_git_repo(repo_path):
                    repositories.append(repo_path)
    else:
        # Recursively search for repositories in subdirectories
        for root, dirs, _ in os.walk(base_path):
            # Skip .git directories to avoid getting into Git internals
            if ".git" in dirs:
                dirs.remove(".git")

            # Check if current directory is a git repo
            root_path = Path(root)
            git_dir = root_path / ".git"
            if git_dir.exists() and git_dir.is_dir():
                repositories.append(root_path)

    # Sort repositories alphabetically by name
    repositories.sort(key=lambda repo: repo.name.lower())

    return repositories


def check_repositories_status(directory="."):
    """Check the status of all git repositories in the given directory."""
    repos = find_git_repositories(directory)

    if not repos:
        print(f"No git repositories found in {directory}")
        return

    print(f"Found {len(repos)} git repositories in {directory}")
    print("-" * 50)

    for repo in repos:
        repo_name = repo.name
        status = get_repo_status(repo)

        if status is None:
            print(f"{repo_name:<30}: Not a valid git repository")
            continue

        if "error" in status:
            print(f"{repo_name:<30}: {status['error']}")
            continue

        print(f"{repo_name:<30} [{status['branch']}]")

        if status["has_changes"]:
            print("  Changes:")
            for line in status["status"].split("\n"):
                line = line.strip()
                if line:
                    print(f"    {line}")
        else:
            print("  No uncommitted changes")

        if status["has_unpushed"]:
            print("  Unpushed commits:")
            for line in status["unpushed"].split("\n"):
                if line:
                    print(f"    {line}")

        print("-" * 50)


def pull_repository(path):
    """Attempt to pull changes for a git repository."""
    if not is_git_repo(path):
        return {"status": "not_a_repo"}

    # Check for local changes
    status = get_repo_status(path)
    if status and status["has_changes"]:
        return {"status": "local_changes"}

    try:
        # Attempt to pull changes
        subprocess.run(
            [GIT_EXECUTABLE, "pull"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        return {"status": "success"}
    except subprocess.CalledProcessError:
        return {"status": "pull_failed"}


def pull_repositories(directory="."):
    """Attempt to pull changes for all git repositories in the given directory."""
    repos = find_git_repositories(directory)

    if not repos:
        print(f"No git repositories found in {directory}")
        return

    print(f"Attempting to pull changes for {len(repos)} git repositories in {directory}")
    print("-" * 50)

    total = len(repos)
    completed = 0
    results = []

    # Print initial progress
    sys.stdout.write(f"Pulling repositories [0/{total}]\r")
    sys.stdout.flush()

    with ThreadPoolExecutor() as executor:
        # Start all repository pull tasks
        future_to_repo = {executor.submit(pull_repository, repo): repo for repo in repos}

        # Process results as they complete
        for future in as_completed(future_to_repo):
            repo = future_to_repo[future]
            repo_name = repo.name
            completed += 1

            # Update progress counter (same line)
            sys.stdout.write(f"Pulling repositories [{completed}/{total}]\r")
            sys.stdout.flush()

            try:
                result = future.result()
                results.append((repo_name, result, None))
            except Exception as exc:
                results.append((repo_name, {"status": "error"}, exc))

    # Print a newline after progress is complete
    print()

    # Sort results alphabetically by repository name
    results.sort(key=lambda x: x[0].lower())

    print("-" * 50)
    for repo_name, result, exc in results:
        if result["status"] == "not_a_repo":
            print(f"{repo_name:<30}: Not a valid git repository")
        elif result["status"] == "local_changes":
            print(f"{repo_name:<30}: Skipped (local changes present)")
        elif result["status"] == "success":
            print(f"{repo_name:<30}: Pull successful")
        elif result["status"] == "pull_failed":
            print(f"{repo_name:<30}: Pull failed")
        elif result["status"] == "error":
            print(f"{repo_name:<30}: Error during pull: {exc}")

    print("-" * 50)


def push_repository(path):
    """Attempt to push changes for a git repository."""
    if not is_git_repo(path):
        return {"status": "not_a_repo"}

    try:
        # Attempt to push changes
        subprocess.run(
            [GIT_EXECUTABLE, "push"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        return {"status": "success"}
    except subprocess.CalledProcessError:
        return {"status": "push_failed"}


def push_repositories(directory="."):
    """Attempt to push changes for all git repositories in the given directory."""
    repos = find_git_repositories(directory)

    if not repos:
        print(f"No git repositories found in {directory}")
        return

    print(f"Attempting to push changes for {len(repos)} git repositories in {directory}")
    print("-" * 50)

    total = len(repos)
    completed = 0
    results = []

    # Print initial progress
    sys.stdout.write(f"Pushing repositories [0/{total}]\r")
    sys.stdout.flush()

    with ThreadPoolExecutor() as executor:
        # Start all repository push tasks
        future_to_repo = {executor.submit(push_repository, repo): repo for repo in repos}

        # Process results as they complete
        for future in as_completed(future_to_repo):
            repo = future_to_repo[future]
            repo_name = repo.name
            completed += 1

            # Update progress counter (same line)
            sys.stdout.write(f"Pushing repositories [{completed}/{total}]\r")
            sys.stdout.flush()

            try:
                result = future.result()
                results.append((repo_name, result, None))
            except Exception as exc:
                results.append((repo_name, {"status": "error"}, exc))

    # Print a newline after progress is complete
    print()

    # Sort results alphabetically by repository name
    results.sort(key=lambda x: x[0].lower())

    print("-" * 50)
    for repo_name, result, exc in results:
        if result["status"] == "not_a_repo":
            print(f"{repo_name:<30}: Not a valid git repository")
        elif result["status"] == "success":
            print(f"{repo_name:<30}: Push successful")
        elif result["status"] == "push_failed":
            print(f"{repo_name:<30}: Push failed (conflict or other issue)")
        elif result["status"] == "error":
            print(f"{repo_name:<30}: Error during push: {exc}")

    print("-" * 50)


def log_repository(path, max_commits=10):
    """Get the commit log for a git repository."""
    if not is_git_repo(path):
        return {"status": "not_a_repo"}

    # Validate max_commits is an integer
    try:
        max_commits_int = int(max_commits)
    except (ValueError, TypeError):
        return {"status": "invalid_max_commits"}
    if max_commits_int < 1:
        return {"status": "invalid_max_commits"}

    try:
        # Get the commit log
        log_process = subprocess.run(
            [GIT_EXECUTABLE, "log", f"--max-count={max_commits_int}", "--oneline"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        return {"status": "success", "log": log_process.stdout.strip()}
    except subprocess.CalledProcessError:
        return {"status": "log_failed"}


def log_repositories(directory=".", max_commits=10):
    """Display the commit log for all git repositories in the given directory."""
    repos = find_git_repositories(directory)

    if not repos:
        print(f"No git repositories found in {directory}")
        return

    print(f"Displaying commit logs for {len(repos)} git repositories in {directory}")
    print("-" * 50)

    for repo in repos:
        repo_name = repo.name
        result = log_repository(repo, max_commits)

        if result["status"] == "not_a_repo":
            print(f"{repo_name:<30}: Not a valid git repository")
        elif result["status"] == "success":
            print(f"{repo_name}:")
            print(result["log"])
        elif result["status"] == "log_failed":
            print(f"{repo_name:<30}: Failed to retrieve log")

        print("-" * 50)
