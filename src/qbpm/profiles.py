from functools import partial
from pathlib import Path

from . import Profile
from .config import Config, find_qutebrowser_config_dir
from .desktop import create_desktop_file
from .log import error, info

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
    if not profile.check_name():
        return False

    if not overwrite and profile.root.exists():
        error(f"{profile.root} already exists")
        return False

    config_dir = profile.root / "config"
    config_dir.mkdir(parents=True, exist_ok=overwrite)
    return True


def create_config(
    profile: Profile,
    qb_config_dir: Path,
    config_py_template: str,
    home_page: str | None = None,
    overwrite: bool = False,
) -> None:
    source = qb_config_dir / "config.py"
    if not source.is_file():
        return
    user_config = profile.root / "config" / "config.py"
    if overwrite and user_config.exists():
        back_up(user_config)
    with user_config.open(mode="w" if overwrite else "x") as dest_config:
        out = partial(print, file=dest_config)
        out(
            config_py_template.format(
                profile_name=profile.name,
                source_config_py=source,
            )
        )
        # TODO move to template?
        if home_page:
            out(f"c.url.start_pages = ['{home_page}']")


def link_autoconfig(
    profile: Profile,
    qb_config_dir: Path,
    overwrite: bool = False,
) -> None:
    if not hasattr(Path, "symlink_to"):
        return
    source = qb_config_dir / "autoconfig.yml"
    dest = profile.root / "config" / "autoconfig.yml"
    if not source.is_file() or dest.resolve() == source.resolve():
        return
    if overwrite and dest.exists():
        back_up(dest)
    dest.symlink_to(source)


def back_up(dest: Path) -> None:
    backup = Path(str(dest) + ".bak")
    info(f"backing up existing {dest.name} to {backup}")
    dest.replace(backup)


def check(profile: Profile) -> bool:
    if not profile.check_name():
        return False
    exists = profile.root.exists()
    if not exists:
        error(f"{profile.root} does not exist")
        return False
    if not profile.root.is_dir():
        error(f"{profile.root} is not a directory")
        return False
    if not (profile.root / "config").is_dir():
        error(f"no config directory in {profile.root}, is it a profile?")
        return False
    return True


def new_profile(
    profile: Profile,
    config: Config,
    home_page: str | None = None,
    overwrite: bool = False,
) -> bool:
    qb_config_dir = config.qutebrowser_config_directory
    if qb_config_dir and not qb_config_dir.is_dir():
        error(f"{qb_config_dir} is not a directory")
        return False
    qb_config_dir = find_qutebrowser_config_dir(
        qb_config_dir, config.symlink_autoconfig
    )
    if not qb_config_dir:
        return False
    if not config.config_py_template:
        error("no value for config_py_template in config.toml")
        return False
    if create_profile(profile, overwrite):
        create_config(
            profile, qb_config_dir, config.config_py_template, home_page, overwrite
        )
        if config.symlink_autoconfig:
            link_autoconfig(profile, qb_config_dir, overwrite)
        if config.generate_desktop_file:
            create_desktop_file(profile, config.desktop_file_directory)
        print(profile.root)
        return True
    return False
