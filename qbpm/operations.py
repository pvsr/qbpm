import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from qbpm import profiles
from qbpm.utils import error


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


def launch(profile_name: str, strict: bool, foreground: bool) -> bool:
    profile = profiles.ensure_profile_exists(profile_name, not strict)
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
