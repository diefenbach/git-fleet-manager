# git-fleet-manager

git-fleet-manager is a command-line tool for managing multiple Git repositories at once. It allows you to perform common Git operations such as checking the status, pulling, pushing, and viewing commit logs across multiple repositories in a specified directory.

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/diefenbach/git-fleet-manager)
[![Test](https://github.com/diefenbach/git-fleet-manager/actions/workflows/test.yml/badge.svg)](https://github.com/diefenbach/git-fleet-manager/actions/workflows/test.yml)

## Features

- **Recursive Repository Discovery**: Automatically finds all Git repositories in a directory and its subdirectories.
- **Selective Repository Management**: Use a `.gfm` file to specify which repositories to manage.
- **Batch Operations**:
  - Check the status of all repositories.
  - Pull changes from remote repositories.
  - Push changes to remote repositories.
  - View commit logs for all repositories.

## Installation

1. Install git-fleet-manager using pip:
    ```bash
    pip install git-fleet-manager
    ```

2. Verify the installation:
    ```bash
    gfm --version
    ```

3. git-fleet-manager is now ready to use. Run the `gfm` command from anywhere in your terminal.


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

5. Display the version of git-fleet-manager:
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

git-fleet-manager was developed to simplify the management of multiple Git repositories, making it easier to perform batch operations efficiently.
