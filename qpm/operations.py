import os
import shutil
import subprocess
from typing import Iterable, Optional

from qpm import profiles
from qpm.profiles import Profile
from qpm.utils import error


def from_session(
    session_name: str, profile_name: Optional[str] = None
) -> Optional[Profile]:
    session = profiles.main_data_dir / "sessions" / (session_name + ".yml")
    if not session.is_file():
        error(f"{session} is not a file")
        return None

    profile = Profile(profile_name or session_name, None)
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
