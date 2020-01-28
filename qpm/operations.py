import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, Optional

from qpm import config, profiles
from qpm.profiles import Profile
from qpm.utils import error


def from_session(
    session_name: str, profile_name: Optional[str] = None
) -> Optional[Path]:
    session = profiles.main_data_dir / "sessions" / (session_name + ".yml")
    if not session.is_file():
        error(f"{session} is not a file")
        return None

    profile_root = profiles.new_profile(profile_name or session_name)
    if not profile_root:
        return None

    session_dir = profile_root / "data" / "sessions"
    session_dir.mkdir(parents=True)
    shutil.copy(session, session_dir / "_autosave.yml")

    return profile_root


def launch(
    profile: Profile, strict: bool, foreground: bool, args: Iterable[str]
) -> bool:
    profile_root = profiles.ensure_profile_exists(profile, not strict)
    if not profile_root:
        return False

    if foreground:
        os.execlp("qutebrowser", "qutebrowser", "-B", str(profile_root), *args)
    else:
        p = subprocess.Popen(
            ["qutebrowser", "-B", str(profile_root), *args],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        try:
            # give qb a chance to validate input before returning to shell
            stdout, stderr = p.communicate(timeout=0.1)
            print(stderr.decode(errors="ignore"), end="")
        except subprocess.TimeoutExpired:
            pass

    return True


def list_() -> None:
    for profile in config.profiles_dir.iterdir():
        print(profile.name)
