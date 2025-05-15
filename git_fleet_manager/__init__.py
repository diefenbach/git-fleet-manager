try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError  # type: ignore

try:
    __version__ = version("git_fleet_manager")
except PackageNotFoundError:
    __version__ = "unknown"
