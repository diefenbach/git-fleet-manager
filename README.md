# git-fleet-manager

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/diefenbach/git-fleet-manager)
[![PyPI](https://img.shields.io/pypi/v/git-fleet-manager?label=PyPI)](https://pypi.org/project/git-fleet-manager/)
[![Python Versions](https://img.shields.io/badge/python-%3E%3D3.8-blue)](https://www.python.org/downloads/)
[![Test](https://github.com/diefenbach/git-fleet-manager/actions/workflows/test.yml/badge.svg)](https://github.com/diefenbach/git-fleet-manager/actions/workflows/test.yml)

git-fleet-manager is a command-line tool for managing multiple Git repositories at once. It allows you to perform common Git operations such as checking the status, pulling, pushing, and viewing commit logs across multiple repositories in a specified directory.

## Motivation

When working on projects that involve multiple independent repositories, managing them individually can become tedious and error-prone. git-fleet-manager (gfm) was created to solve this problem by providing a unified interface to perform Git operations across all repositories simultaneously.

This is particularly useful for:
- Microservice architectures where each service has its own repository
- Monorepo alternatives where related projects are kept in separate repositories
- Development environments that require working with multiple interdependent projects
- Teams that need to ensure consistent state across a collection of repositories

Instead of manually navigating to each repository directory to check status, pull updates, or push changes, git-fleet-manager lets you perform these operations in a single command, saving time and reducing the chance of overlooking repositories.


## Features

- **Recursive Repository Discovery**: Automatically finds all Git repositories in a directory and its subdirectories.
- **Selective Repository Management**: Use a `.gfm` file to specify which repositories to manage.
- **Batch Operations**:
  - Check the status of all repositories.
  - Pull changes from remote repositories.
  - Push changes to remote repositories.
  - View commit logs for all repositories.
  - Checkout branches across repositories.

## Installation

You can install git-fleet-manager as a tool using uv (recommended):

```bash
uv tool install git-fleet-manager
```

Alternatively, you can install git-fleet-manager using pip:

### From PyPI
```bash
pip install git-fleet-manager
```

### From GitHub (latest development version)
```bash
pip install git+https://github.com/diefenbach/git-fleet-manager.git
```

Verify the installation:
    ```bash
    gfm --version
    ```

git-fleet-manager is now ready to use. Run the `gfm` command from anywhere in your terminal.


## Usage

Run the `gfm` command with the desired subcommand and options.

### Commands

#### `status`
Check the status of all repositories in the specified directory.

```bash
gfm status [directory]
```

- **directory**: The directory to scan for repositories (default: current directory).

#### `pull`
Pull changes for all repositories in the specified directory.

```bash
gfm pull [directory]
```

- **directory**: The directory to scan for repositories (default: current directory).

#### `push`
Push changes for all repositories in the specified directory.

```bash
gfm push [directory]
```

- **directory**: The directory to scan for repositories (default: current directory).

#### `log`
View the commit log for all repositories in the specified directory.

```bash
gfm log [directory] [--max-commits MAX_COMMITS]
```

- **directory**: The directory to scan for repositories (default: current directory).
- **--max-commits**: The maximum number of commits to display for each repository (default: 10).

#### `checkout`
Checkout a specific branch for all repositories in the specified directory. Repositories where the branch doesn't exist will be automatically skipped.

```bash
gfm checkout [directory] --branch BRANCH_NAME
```

- **directory**: The directory to scan for repositories (default: current directory).
- **--branch**: The name of the branch to checkout (required).

#### `--version`
Display the current version of git-fleet-manager.

```bash
gfm --version
```

### `.gfm` File

If a `.gfm` file exists in the specified directory, only the repositories listed in the file will be managed. The file should contain one repository path per line, relative to the directory containing the `.gfm` file.

Example `.gfm` file:
```
repo1
subdir/repo2
```

### Examples

1. Check the status of all repositories in the current directory:
   ```bash
   gfm status
   ```

2. Pull changes for all repositories in `/projects`:
   ```bash
   gfm pull /projects
   ```

3. Push changes for repositories listed in a `.gfm` file:
   ```bash
   gfm push /projects
   ```

4. View the last 5 commits for all repositories:
   ```bash
   gfm log /projects --max-commits 5
   ```

5. Checkout the 'develop' branch for all repositories:
   ```bash
   gfm checkout /projects --branch develop
   ```

6. Display the version of git-fleet-manager:
   ```bash
   gfm --version
   ```

## Project Structure

```
git_fleet_manager/
├── git_utils.py       # Utility functions for Git operations
├── cli.py             # Command-line interface for git-fleet-manager
└── __init__.py        # Package initialization and versioning

.github/
└── workflows/         # GitHub Actions workflow files
    ├── test.yml       # CI workflow for testing
    └── publish.yml    # CD workflow for PyPI publishing
```

## Source Code

The source code is available on GitHub at [https://github.com/diefenbach/git-fleet-manager](https://github.com/diefenbach/git-fleet-manager).

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve git-fleet-manager.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

This project was created with the assistance of AI tools, including code generation and documentation support.

git-fleet-manager was developed to simplify the management of multiple Git repositories, making it easier to perform batch operations efficiently.

## Publish a new version

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with new changes
3. Commit changes: `git commit -am "Bump version to x.y.z"`
4. Create a tag: `git tag x.y.z`
5. Push changes: `git push origin main`
6. Push tags: `git push origin --tags`
7. Go to GitHub [https://github.com/diefenbach/git-fleet-manager](https://github.com/diefenbach/git-fleet-manager) and create a new release using the tag
