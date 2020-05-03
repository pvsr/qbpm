from pathlib import Path

from xdg import BaseDirectory  # type: ignore

profiles_dir = Path(BaseDirectory.xdg_data_home) / "qutebrowser-profiles"
