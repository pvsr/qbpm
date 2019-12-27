import platform
import shutil
import sys
from pathlib import Path
from typing import Optional

from xdg import BaseDirectory  # type: ignore

main_config_dir = Path(BaseDirectory.save_config_path("qutebrowser"))
profiles_dir = Path(BaseDirectory.save_data_path("qutebrowser-profiles"))

if platform.system() == "Linux":
    main_data_dir = Path(BaseDirectory.save_data_path("qutebrowser"))
elif platform.system() == "Darwin":
    main_data_dir = Path.home() / "Library" / "Application Support" / "qutebrowser"
else:
    error("lol")
    sys.exit(1)


def create_profile(profile_name: str) -> Optional[Path]:
    profile_root = profiles_dir / profile_name

    if profile_root.exists():
        error(f"{profile_root} already exists")
        return None

    config_dir = profile_root / "config"
    config_dir.mkdir(parents=True)
    return profile_root


def create_config(profile_root: Path) -> None:
    with (profile_root / "config" / "config.py").open(mode="x") as conf:
        print(f"config.source('{main_config_dir / 'config.py'}')", file=conf)


def new_profile(profile_name: str) -> Optional[Path]:
    profile_root = create_profile(profile_name)
    if not profile_root:
        return None

    create_config(profile_root)
    return profile_root


def from_session(
    session_name: str, profile_name: Optional[str] = None
) -> Optional[Path]:
    session = main_data_dir / "sessions" / (session_name + ".yml")
    if not session.is_file():
        error(f"{session} is not a file")
        return None

    profile_root = new_profile(profile_name or session_name)
    if not profile_root:
        return None

    session_dir = profile_root / "data" / "sessions"
    session_dir.mkdir(parents=True)
    shutil.copy(session, session_dir / "_autosave.yml")

    return profile_root


def error(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
