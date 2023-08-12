import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from sys import platform
from typing import Optional

from xdg import BaseDirectory

from . import Profile, profiles
from .icons import find_icon_file
from .utils import AUTO_MENUS, error, installed_menus


def from_session(
    profile: Profile,
    session_path: Path,
    desktop_file: bool = True,
    overwrite: bool = False,
) -> bool:
    if not profiles.new_profile(profile, None, desktop_file, overwrite):
        return False

    session_dir = profile.root / "data" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=overwrite)
    shutil.copy(session_path, session_dir / "_autosave.yml")

    return True


def launch(
    profile: Profile, create: bool, foreground: bool, qb_args: tuple[str, ...]
) -> bool:
    if not profiles.ensure_profile_exists(profile, create):
        return False

    args = profile.cmdline() + list(qb_args)
    if not shutil.which(args[0]):
        error("qutebrowser is not installed")
        return False

    if foreground:
        return subprocess.run(args, check=False).returncode == 0
    else:
        p = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        try:
            # give qb a chance to validate input before returning to shell
            stdout, stderr = p.communicate(timeout=0.1)
            print(stderr.decode(errors="ignore"), end="")
        except subprocess.TimeoutExpired:
            pass

    return True


application_dir = Path(BaseDirectory.xdg_data_home) / "applications" / "qbpm"


def desktop(profile: Profile) -> bool:
    exists = profile.exists()
    if exists:
        profiles.create_desktop_file(profile)
    else:
        error(f"profile {profile.name} not found at {profile.root}")
    return exists


def choose(
    profile_dir: Path,
    menu: str,
    foreground: bool,
    qb_args: tuple[str, ...],
    force_icon: bool,
) -> bool:
    menu = menu or next(installed_menus())
    if not menu:
        error(f"No menu program found, please install one of: {AUTO_MENUS}")
        return False
    if menu == "applescript" and platform != "darwin":
        error(f"Menu applescript cannot be used on a {platform} host")
        return False
    profiles = [
        Profile(profile.name, profile_dir) for profile in sorted(profile_dir.iterdir())
    ]
    if len(profiles) == 0:
        error("No profiles")
        return False

    menu_cmd = menu_command(menu, profiles, qb_args)
    if not menu_cmd:
        return False

    menu_items = build_menu_items(profiles, menu_cmd.icon_support or force_icon)

    selection_cmd = subprocess.run(
        menu_cmd.command,
        input=menu_items,
        text=True,
        # TODO remove shell dependency
        shell=True,
        stdout=subprocess.PIPE,
        stderr=None,
        check=False,
    )
    out = selection_cmd.stdout
    selection = out and out.rstrip("\n")

    if selection:
        profile = Profile(selection, profile_dir)
        return launch(profile, False, foreground, qb_args)
    else:
        error("No profile selected")
        return False


@dataclass
class Menu:
    command: str
    icon_support: bool


def menu_command(
    menu: str, profiles: list[Profile], qb_args: tuple[str, ...]
) -> Optional[Menu]:
    icon = False
    arg_string = " ".join(qb_args)
    if menu == "applescript":
        profile_list = '", "'.join([p.name for p in profiles])
        return Menu(
            f"""osascript -e \'set profiles to {{"{profile_list}"}}
set profile to choose from list profiles with prompt "qutebrowser: {arg_string}" default items {{item 1 of profiles}}
item 1 of profile\'""",
            icon,
        )

    prompt = "-p qutebrowser"
    command = menu
    # TODO arg
    if len(menu.split(" ")) == 1:
        program = Path(menu).name
        if program == "rofi":
            icon = True
            command = f"{menu} -dmenu -no-custom {prompt} -mesg '{arg_string}'"
        elif program == "wofi":
            command = f"{menu} --dmenu {prompt}"
        elif program.startswith("dmenu"):
            command = f"{menu} {prompt}"
        elif program.startswith("fzf"):
            command = f"{menu} --prompt 'qutebrowser '"
        elif program == "fuzzel":
            icon = True
            command = f"{menu} -d"
    exe = command.split(" ")[0]
    if not shutil.which(exe):
        error(f"command '{exe}' not found")
        return None
    return Menu(command, icon)


def build_menu_items(profiles: list[Profile], icon: bool) -> str:
    if icon and any(icons := [find_icon_file(p) for p in profiles]):
        menu_items = [
            f"{p.name}\0icon\x1f{icon or 'qutebrowser'}"
            for (p, icon) in zip(profiles, icons)
        ]
    else:
        menu_items = [p.name for p in profiles]

    return "\n".join(menu_items)
