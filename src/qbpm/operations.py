import shutil
from pathlib import Path

from . import Profile, icons, profiles
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
        create_desktop_file(profile, icon=icons.icon_for_profile(profile))
    return exists


def icon(profile: Profile, icon: str, by_name: bool, overwrite: bool) -> bool:
    if not profiles.check(profile):
        return False
    if by_name:
        icon_id = icon if icons.install_icon_by_name(profile, icon, overwrite) else None
    else:
        if Path(icon).is_file():
            icon_file = icons.install_icon_file(profile, Path(icon), overwrite)
        else:
            icon_file = icons.download_icon(profile, icon, overwrite)
        icon_id = str(icon_file) if icon_file else None
    if icon_id:
        profiles.add_to_desktop_file(profile, "Icon", icon_id)
    return icon_id is not None
