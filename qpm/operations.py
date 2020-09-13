import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, Optional

from xdg import BaseDirectory  # type: ignore

from qpm import profiles
from qpm.profiles import Profile
from qpm.utils import error


def from_session(
    session: str,
    profile_name: Optional[str] = None,
    profile_dir: Optional[Path] = None,
) -> Optional[Profile]:
    if session.endswith(".yml"):
        session_file = Path(session).expanduser()
        session_name = session_file.stem
    else:
        session_name = session
        session_file = profiles.main_data_dir / "sessions" / (session_name + ".yml")
    if not session_file.is_file():
        error(f"{session_file} is not a file")
        return None

    profile = Profile(profile_name or session_name, profile_dir)
    if not profiles.new_profile(profile):
        return None

    session_dir = profile.root / "data" / "sessions"
    session_dir.mkdir(parents=True)
    shutil.copy(session_file, session_dir / "_autosave.yml")

    return profile


def launch(
    profile: Profile, strict: bool, foreground: bool, qb_args: Iterable[str]
) -> bool:
    if not profiles.ensure_profile_exists(profile, not strict):
        return False

    if foreground:
        os.execlp("qutebrowser", "qutebrowser", "-B", str(profile.root), *qb_args)
    else:
        p = subprocess.Popen(
            ["qutebrowser", "-B", str(profile.root), *qb_args],
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


DEFAULT_PROFILE_DIR = Path(BaseDirectory.xdg_data_home) / "qutebrowser-profiles"


def list_() -> None:
    for profile in DEFAULT_PROFILE_DIR.iterdir():
        print(profile.name)
