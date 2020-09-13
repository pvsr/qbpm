import platform
import sys
from pathlib import Path
from typing import Optional
from textwrap import dedent

from xdg import BaseDirectory  # type: ignore

from qpm.utils import error


class Profile:
    name: str
    profile_dir: Path
    root: Path

    def __init__(self, name: str, profile_dir: Optional[Path]) -> None:
        self.name = name
        self.profile_dir = profile_dir or Path(
            BaseDirectory.save_data_path("qutebrowser-profiles")
        )
        self.root = self.profile_dir / name

    def check(self) -> Optional["Profile"]:
        if not self.profile_dir.resolve().is_dir():
            error("{self.profile_dir} is not a directory")
            return None
        if self.profile_dir.resolve() not in self.root.resolve().parents:
            error("will not create profile outside of profile dir. consider using -P")
            return None
        if self.root.exists():
            error(f"{self.root} already exists")
            return None
        for parent in self.root.parents:
            if parent == self.profile_dir:
                break
            if parent.exists():
                error(f"{parent} already exists")
                return None
        return self


main_config_dir = Path(BaseDirectory.xdg_config_home) / "qutebrowser"

if platform.system() == "Linux":
    main_data_dir = Path(BaseDirectory.xdg_data_home) / "qutebrowser"
elif platform.system() == "Darwin":
    main_data_dir = Path.home() / "Library" / "Application Support" / "qutebrowser"
else:
    error("lol")
    sys.exit(1)


def create_profile(profile: Profile) -> bool:
    if not profile.check():
        return False

    config_dir = profile.root / "config"
    config_dir.mkdir(parents=True)
    return True


def create_config(profile: Profile, home_page: Optional[str] = None) -> None:
    user_config = profile.root / "config" / "config.py"
    with user_config.open(mode="x") as dest_config:
        title_prefix = "{perc}{current_title}{title_sep}"
        config = (
            f"c.window.title_format = '{title_prefix} qutebrowser ({profile.name})'"
        )
        if home_page:
            config = config + f"\nc.url.default_page = '{home_page}'"
            config = config + f"\nc.url.start_pages = ['{home_page}']"
        print(dedent(config), file=dest_config)
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


def new_profile(profile: Profile, home_page: Optional[str] = None) -> bool:
    if create_profile(profile):
        create_config(profile, home_page)
        return True
    return False
