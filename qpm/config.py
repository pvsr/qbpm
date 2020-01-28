from pathlib import Path

from xdg import BaseDirectory  # type: ignore

profiles_dir = Path(BaseDirectory.save_data_path("qutebrowser-profiles"))
