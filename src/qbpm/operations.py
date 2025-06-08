import shutil
from pathlib import Path

from . import Profile, profiles
from .config import Config
from .desktop import create_desktop_file


def from_session(
    profile: Profile,
    session_path: Path,
    config: Config,
    overwrite: bool = False,
) -> bool:
    if not profiles.new_profile(profile, config, None, overwrite):
        return False

    session_dir = profile.root / "data" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=overwrite)
    shutil.copy(session_path, session_dir / "_autosave.yml")

    return True


def desktop(profile: Profile, application_dir: Path) -> bool:
    exists = profiles.check(profile)
    if exists:
        create_desktop_file(profile, application_dir)
    return exists
