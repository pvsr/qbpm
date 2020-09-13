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
    session_name: str,
    profile_name: Optional[str] = None,
    profile_dir: Optional[Path] = None,
) -> Optional[Profile]:
    session = profiles.main_data_dir / "sessions" / (session_name + ".yml")
    if not session.is_file():
        error(f"{session} is not a file")
        return None

    profile = Profile(profile_name or session_name, profile_dir)
    if not profiles.new_profile(profile):
        return None

    session_dir = profile.root / "data" / "sessions"
    session_dir.mkdir(parents=True)
    shutil.copy(session, session_dir / "_autosave.yml")

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
