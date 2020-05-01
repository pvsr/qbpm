import platform
import sys
from pathlib import Path

from xdg import BaseDirectory  # type: ignore

from qpm import config
from qpm.utils import error


class Profile:
    name: str
    root: Path

    def __init__(self, name: str) -> None:
        self.name = name
        self.root = config.profiles_dir / name


main_config_dir = Path(BaseDirectory.save_config_path("qutebrowser"))

if platform.system() == "Linux":
    main_data_dir = Path(BaseDirectory.save_data_path("qutebrowser"))
elif platform.system() == "Darwin":
    main_data_dir = Path.home() / "Library" / "Application Support" / "qutebrowser"
else:
    error("lol")
    sys.exit(1)


def check_profile(profile_root: Path) -> bool:
    if config.profiles_dir.resolve() not in profile_root.resolve().parents:
        error("will not create profile outside of profile dir. consider using -P")
        return False
    if profile_root.exists():
        error(f"{profile_root} already exists")
        return False
    for parent in profile_root.parents:
        if parent == config.profiles_dir:
            break
        if parent.exists():
            error(f"{parent} already exists")
            return False
    return True


def create_profile(profile: Profile) -> bool:
    if not check_profile(profile.root):
        return False

    config_dir = profile.root / "config"
    config_dir.mkdir(parents=True)
    return True


def create_config(profile: Profile) -> None:
    with (profile.root / "config" / "config.py").open(mode="x") as dest_config:
        print(
            "c.window.title_format = '{perc}{current_title}{title_sep}"
            + f"qutebrowser ({profile.name})'",
            file=dest_config,
        )
        print(f"config.source('{main_config_dir / 'config.py'}')", file=dest_config)
        for conf in main_config_dir.glob("conf.d/*.py"):
            print(f"config.source('{conf}')", file=dest_config)


def ensure_profile_exists(profile: Profile, create: bool = True) -> bool:
    if profile.root.exists() and not profile.root.is_dir():
        error(f"{profile.root} is not a directory")
        return False
    if not profile.root.exists() and create:
        return new_profile(profile)
    if not profile.root.exists():
        error(f"{profile.root} does not exist")
        return False
    return True


def new_profile(profile: Profile) -> bool:
    if create_profile(profile):
        create_config(profile)
        return True
    return False
