import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Union

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


def get_profile_root(profile_name: str) -> Path:
    return profiles_dir / profile_name


def create_profile(profile: Union[str, Path]) -> Optional[Path]:
    if isinstance(profile, str):
        profile_root = get_profile_root(profile)
    else:
        profile_root = profile

    if profile_root.exists():
        error(f"{profile_root} already exists")
        return None

    config_dir = profile_root / "config"
    config_dir.mkdir(parents=True)
    return profile_root


def create_config(profile_root: Path) -> None:
    with (profile_root / "config" / "config.py").open(mode="x") as conf:
        print(f"config.source('{main_config_dir / 'config.py'}')", file=conf)


def new_profile(profile: Union[str, Path]) -> Optional[Path]:
    profile_root = create_profile(profile)
    if profile_root:
        create_config(profile_root)

    return profile_root


def ensure_profile_exists(profile_name: str, create: bool = True) -> Optional[Path]:
    profile = get_profile_root(profile_name)
    if profile.exists() and not profile.is_dir():
        error(f"{profile} is not a directory")
        return None
    elif not profile.exists():
        if create:
            return new_profile(profile)
        else:
            error(f"{profile} does not exist")
            return None
    else:
        return profile


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


def launch(profile_name: str, strict: bool, foreground: bool) -> bool:
    profile = ensure_profile_exists(profile_name, not strict)
    if not profile:
        return False

    if foreground:
        os.execlp("qutebrowser", "qutebrowser", "-B", str(profile))
    else:
        subprocess.Popen(
            ["qutebrowser", "-B", str(profile)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    return True


def error(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
