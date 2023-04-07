import shutil
from pathlib import Path

from . import Profile, icons, profiles
from .desktop import create_desktop_file, add_to_desktop_file

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
        add_to_desktop_file(profile, "Icon", icon_id)
    return icon_id is not None
