from pathlib import Path
from textwrap import dedent
from typing import List, Optional

from xdg import BaseDirectory  # type: ignore
from xdg.DesktopEntry import DesktopEntry  # type: ignore

from qpm.utils import error, user_config_dir


class Profile:
    name: str
    profile_dir: Path
    set_app_id: bool
    root: Path

    def __init__(
        self, name: str, profile_dir: Optional[Path], set_app_id: bool = False
    ) -> None:
        self.name = name
        self.profile_dir = profile_dir or Path(
            BaseDirectory.save_data_path("qutebrowser-profiles")
        )
        self.set_app_id = set_app_id
        self.root = self.profile_dir / name

    def check(self) -> Optional["Profile"]:
        if "/" in self.name:
            error("profile name cannot contain slashes")
            return None
        if not self.profile_dir.resolve().is_dir():
            error(f"{self.profile_dir} is not a directory")
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

    def exists(self) -> bool:
        return self.root.exists() and self.root.is_dir()

    def cmdline(self) -> List[str]:
        return ["qutebrowser", "-B", str(self.root), "--qt-arg", "name", self.name] + (
            ["--desktop-file-name", self.name] if self.set_app_id else []
        )


def create_profile(profile: Profile) -> bool:
    if not profile.check():
        return False

    config_dir = profile.root / "config"
    config_dir.mkdir(parents=True)
    print(profile.root)
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
        main_config_dir = user_config_dir()
        print(dedent(config), file=dest_config)
        print(f"config.source('{main_config_dir / 'config.py'}')", file=dest_config)
        for conf in main_config_dir.glob("conf.d/*.py"):
            print(f"config.source('{conf}')", file=dest_config)


application_dir = Path(BaseDirectory.xdg_data_home) / "applications" / "qpm"


def create_desktop_file(profile: Profile):
    desktop = DesktopEntry(str(application_dir / f"{profile.name}.desktop"))
    desktop.set("Name", f"{profile.name} (qutebrowser profile)")
    # TODO allow passing in an icon value
    desktop.set("Icon", "qutebrowser")
    desktop.set("Exec", " ".join(profile.cmdline()) + " %u")
    desktop.set("Categories", ["Network"])
    desktop.set("Terminal", False)
    desktop.set("StartupNotify", True)
    desktop.write()


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


def new_profile(
    profile: Profile, home_page: Optional[str] = None, desktop_file: bool = True
) -> bool:
    if create_profile(profile):
        create_config(profile, home_page)
        if desktop_file:
            create_desktop_file(profile)
        return True
    return False
