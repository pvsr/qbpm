import re
import shutil
from collections import namedtuple
from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional
from urllib.parse import urlparse

import favicon
import requests
from PIL import Image

from . import Profile, __version__
from .utils import error, info

PREFERRED_ICONS = [
    re.compile(p)
    for p in [
        r"favicon.*\.ico$",
        r"favicon.*\.svg$",
        r"favicon.*\.png$",
        r"\.ico$",
        r"icon\.png$",
        r"\.svg$",
    ]
]

# https://github.com/scottwernervt/favicon/blob/123e431f53b2c4903b540246a85db0b1633d4786/src/favicon/favicon.py#L40
Icon = namedtuple("Icon", ["url", "width", "height", "format"])


def choose_icon(icons: list[Icon]) -> Optional[Icon]:
    for pattern in PREFERRED_ICONS:
        for icon in icons:
            if pattern.search(icon.url):
                info(f"chose {icon.url}")
                return icon
    return None


headers = {"user-agent": f"qbpm/{__version__}"}


def download_icon(profile: Profile, home_page: str, overwrite: bool) -> Optional[Path]:
    if not urlparse(home_page).scheme:
        home_page = f"https://{home_page}"
    try:
        icons = favicon.get(home_page, headers=headers, timeout=10)
    except Exception as e:
        info(str(e))
        error(f"failed to fetch favicon from {home_page}")
        return None
    if not icons:
        error(f"no favicon found on {home_page}")
        return None
    icon = choose_icon(icons)
    if not icon:
        info(f"no favicons found matching one of {PREFERRED_ICONS}")
        return None

    tmp_dir = TemporaryDirectory()
    work_dir = Path(tmp_dir.name)
    work_icon = work_dir / f"favicon.{icon.format}"
    icon_body = requests.get(icon.url, headers=headers, timeout=10)
    with work_icon.open("wb") as icon_file:
        for chunk in icon_body.iter_content(1024):
            icon_file.write(chunk)

    return install_icon_file(profile, work_icon, overwrite, icon.url)


def icon_for_profile(profile: Profile) -> Optional[str]:
    icon_file = next(find_icon_files(profile), None)
    if icon_file and icon_file.suffix == ".name":
        return icon_file.read_text()
    return str(icon_file) if icon_file else None


def install_icon_file(
    profile: Profile, src: Path, overwrite: bool, origin: Optional[str] = None
) -> Optional[Path]:
    if not check_or_replace_existing_icon(profile, overwrite):
        return None
    icon_format = src.suffix
    dest = profile.root / f"icon{icon_format}"
    if icon_format == ".ico":
        dest = dest.with_suffix(".png")
        try:
            image = Image.open(src)
            image.save(dest, icon_format="png")
        except Exception as e:
            info(str(e))
            error(f"failed to convert {origin or src} to png")
            return None
    else:
        shutil.copy(src, dest)
    return dest.absolute()


def install_icon_by_name(profile: Profile, icon_name: str, overwrite: bool) -> bool:
    if not check_or_replace_existing_icon(profile, overwrite):
        return False
    file = profile.root / "icon.name"
    file.write_text(icon_name)
    return True


def check_or_replace_existing_icon(profile: Profile, overwrite: bool) -> bool:
    existing_icons = find_icon_files(profile)
    existing_icon = next(existing_icons, None)
    if not existing_icon:
        return True
    elif overwrite:
        existing_icon.unlink()
        for icon in existing_icons:
            icon.unlink()
        return True
    else:
        error(f"icon already exists in {profile.root}, pass --overwrite to replace it")
        return False


def find_icon_files(profile: Profile) -> Iterator[Path]:
    for ext in ["png", "svg", "name"]:
        icon = profile.root / f"icon.{ext}"
        if icon.is_file():
            yield icon.absolute()
