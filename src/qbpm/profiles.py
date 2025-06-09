from functools import partial
from pathlib import Path
from sys import platform

from . import Profile
from .desktop import create_desktop_file
from .log import error, or_phrase
from .paths import qutebrowser_config_dirs

MIME_TYPES = [
    "text/html",
    "text/xml",
    "application/xhtml+xml",
    "application/xml",
    "application/rdf+xml",
    "image/gif",
    "image/jpeg",
    "image/png",
    "x-scheme-handler/http",
    "x-scheme-handler/https",
    "x-scheme-handler/qute",
]


def create_profile(profile: Profile, overwrite: bool = False) -> bool:
    if not profile.check():
        return False

    if not overwrite and profile.root.exists():
        error(f"{profile.root} already exists")
        return False

    config_dir = profile.root / "config"
    config_dir.mkdir(parents=True, exist_ok=overwrite)
    print(profile.root)
    return True


def create_config(
    profile: Profile,
    qb_config_dir: Path,
    home_page: str | None = None,
    overwrite: bool = False,
) -> None:
    user_config = profile.root / "config" / "config.py"
    with user_config.open(mode="w" if overwrite else "x") as dest_config:
        out = partial(print, file=dest_config)
        out("config.load_autoconfig()")
        title_prefix = "{perc}{current_title}{title_sep}"
        out(f"c.window.title_format = '{title_prefix} qutebrowser ({profile.name})'")
        if home_page:
            out(f"c.url.start_pages = ['{home_page}']")
        out(f"config.source(r'{qb_config_dir / 'config.py'}')")


def exists(profile: Profile) -> bool:
    if profile.root.exists() and not profile.root.is_dir():
        error(f"{profile.root} is not a directory")
        return False
    if not profile.root.exists():
        error(f"{profile.root} does not exist")
        return False
    return True


def new_profile(
    profile: Profile,
    qb_config_dir: Path | None,
    home_page: str | None = None,
    desktop_file: bool | None = None,
    overwrite: bool = False,
) -> bool:
    qb_config_dir = find_qutebrowser_config_dir(qb_config_dir)
    if not qb_config_dir:
        return False
    if create_profile(profile, overwrite):
        create_config(profile, qb_config_dir, home_page, overwrite)
        if desktop_file is True or (desktop_file is not False and platform == "linux"):
            create_desktop_file(profile)
        return True
    return False


def find_qutebrowser_config_dir(qb_config_dir: Path | None) -> Path | None:
    config_file = "config.py"
    dirs = (
        [qb_config_dir, qb_config_dir / "config"]
        if qb_config_dir
        else qutebrowser_config_dirs()
    )
    for config_dir in dirs:
        if (config_dir / config_file).exists():
            return config_dir.absolute()
    error(f"could not find {config_file} in {or_phrase(dirs)}")
    return None
