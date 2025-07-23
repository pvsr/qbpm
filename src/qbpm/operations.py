import shutil
from pathlib import Path

from . import Profile, profiles
from .desktop import create_desktop_file


def from_session(
    profile: Profile,
    session_path: Path,
    qb_config_dir: Path | None,
    desktop_file: bool = True,
    overwrite: bool = False,
) -> bool:
    if not profiles.new_profile(profile, qb_config_dir, None, desktop_file, overwrite):
        return False

    session_dir = profile.root / "data" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=overwrite)
    shutil.copy(session_path, session_dir / "_autosave.yml")

    return True


def desktop(profile: Profile) -> bool:
    exists = profiles.check(profile)
    if exists:
        create_desktop_file(profile)
    return exists
