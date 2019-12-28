import platform
import sys
from pathlib import Path
from typing import Optional, Union

from xdg import BaseDirectory  # type: ignore

from qpm import conf
from qpm.utils import error

# profile name or path
Profile = Union[str, Path]


main_config_dir = Path(BaseDirectory.save_config_path("qutebrowser"))

if platform.system() == "Linux":
    main_data_dir = Path(BaseDirectory.save_data_path("qutebrowser"))
elif platform.system() == "Darwin":
    main_data_dir = Path.home() / "Library" / "Application Support" / "qutebrowser"
else:
    error("lol")
    sys.exit(1)


def get_profile_root(profile: Profile) -> Path:
    if isinstance(profile, str):
        return conf.profiles_dir / profile
    else:
        return profile


def create_profile(profile: Profile) -> Optional[Path]:
    profile_root = get_profile_root(profile)

    if profile_root.exists():
        error(f"{profile_root} already exists")
        return None

    config_dir = profile_root / "config"
    config_dir.mkdir(parents=True)
    return profile_root


def create_config(profile_root: Path) -> None:
    with (profile_root / "config" / "config.py").open(mode="x") as conf:
        print(f"config.source('{main_config_dir / 'config.py'}')", file=conf)


def ensure_profile_exists(profile: Profile, create: bool = True) -> Optional[Path]:
    profile_root = get_profile_root(profile)
    if profile_root.exists() and not profile_root.is_dir():
        error(f"{profile_root} is not a directory")
        return None
    if not profile_root.exists() and create:
        return new_profile(profile_root)
    if not profile_root.exists():
        error(f"{profile_root} does not exist")
        return None
    return profile_root


def new_profile(profile: Profile) -> Optional[Path]:
    profile_root = create_profile(profile)
    if profile_root:
        create_config(profile_root)

    return profile_root
