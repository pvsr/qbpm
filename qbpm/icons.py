import shutil
from collections import namedtuple
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional
from urllib.parse import urlparse

import favicon
import requests
from PIL import Image

from .profiles import Profile

PREFERRED_ICONS = [
    "favicon.ico",
    "favicon.svg",
    "favicon.png",
    ".ico",
]

Icon = namedtuple("Icon", ["url", "width", "height", "format"])


def choose_icon(icons: list[Icon]) -> Optional[Icon]:
    print(f"{icons=}")
    for key in PREFERRED_ICONS:
        for icon in icons:
            if key in icon.url:
                print(f"chose {icon}")
                return icon
    return None


def download_icon(profile: Profile, home_page: str) -> Optional[Path]:
    if not urlparse(home_page).scheme:
        home_page = f"https://{home_page}"
    icons = favicon.get(home_page, timeout=10)
    icon = choose_icon(icons)
    if not icon:
        # TODO print
        return None

    tmp_dir = TemporaryDirectory()
    work_dir = Path(tmp_dir.name)
    work_icon = work_dir / f"favicon.{icon.format}"
    resp = requests.get(icon.url, timeout=10)
    with work_icon.open("wb") as icon_file:
        for chunk in resp.iter_content(1024):
            icon_file.write(chunk)

    icon_path = profile.root / f"icon.{icon.format}"
    if icon.format == "ico":
        icon_path = icon_path.with_suffix(".png")
        image = Image.open(work_icon)
        image.save(icon_path)
    else:
        shutil.move(work_icon, icon_path)

    return icon_path.absolute()


def find_icon_file(profile: Profile) -> Optional[Path]:
    icon_path = next(filter(lambda p: p.is_file(), profile.root.glob("icon.*")), None)
    return icon_path.absolute() if icon_path else icon_path
