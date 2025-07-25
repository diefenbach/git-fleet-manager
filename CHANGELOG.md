# Changelog

All notable changes to git-fleet-manager will be documented in this file.

## [Unreleased]

### Coming soon
- Future features and improvements will be listed here

## [1.0.5] - 2025-07-25

### Added
- Add gfm checkout command: checkout a specific branch across repositories, automatically skipping repositories where the branch doesn't exist


## [1.0.4] - 2025-07-02

### Added
- Add gfm branch command

## [1.0.3] - 2025-07-02

### Added
- gfm log: display date for every commit

## [1.0.2] - 2025-05-31

### Changed
- Switching to uv.

## [0.1.3] - 2025-05-15

### Added
- Added GitHub Actions workflows for CI/CD:
  - Automated testing on multiple Python versions and platforms
  - Publish to PyPI on new releases

## [0.1.2] - 2025-05-15

### Added
- Improved progress indicator for pull and push operations showing real-time updates on a single line

### Changed
- Simplified user interface with cleaner output formatting
- Update dependencies and documentation

## [0.1.1] - 2025-05-15

### Added
- Progress indicator for pull and push operations showing [current/total] count
- Parallel execution of Git operations for improved performance

## [0.1.0] - 2025-05-15

### Added
- Initial public release
- Command-line interface with commands for: status, pull, push, and log
- Recursive discovery of Git repositories in a directory
- Support for selective repository management with `.gfm` file

### Fixed
- Initial bugs and improved error handling
