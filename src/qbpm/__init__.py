from pathlib import Path

from .log import error
from .paths import qutebrowser_exe

try:
    from qbpm.version import version as __version__  # type: ignore
except ImportError:
    __version__ = "unknown"


class Profile:
    name: str
    profile_dir: Path
    root: Path

    def __init__(self, name: str, profile_dir: Path) -> None:
        self.name = name
        self.profile_dir = profile_dir
        self.root = self.profile_dir / name

    def check_name(self) -> bool:
        if "/" in self.name or self.name in [".", ".."]:
            error("profile name cannot be a path")
            return False
        return True

    def cmdline(self) -> list[str]:
        return [
            qutebrowser_exe(),
            "-B",
            str(self.root),
            "--qt-arg",
            "name",
            self.name,
            "--desktop-file-name",
            self.name,
        ]
