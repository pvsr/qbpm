try:
    from qbpm.version import version as __version__  # type: ignore
except ImportError:
    __version__ = "unknown"
