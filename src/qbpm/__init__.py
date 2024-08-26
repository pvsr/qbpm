from pathlib import Path
from typing import Optional

from xdg import BaseDirectory

from .utils import error, qutebrowser_exe

try:
    from qbpm.version import version as __version__  # type: ignore
except ImportError:
    __version__ = "unknown"


class Profile:
    name: str
    profile_dir: Path
    root: Path

    def __init__(self, name: str, profile_dir: Optional[Path]) -> None:
        self.name = name
        self.profile_dir = profile_dir or Path(
            BaseDirectory.save_data_path("qutebrowser-profiles")
        )
        self.root = self.profile_dir / name

    def check(self) -> Optional["Profile"]:
        if "/" in self.name:
            error("profile name cannot contain slashes")
            return None
        return self

    def exists(self) -> bool:
        return self.root.exists() and self.root.is_dir()

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
