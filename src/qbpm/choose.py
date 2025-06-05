import shutil
import subprocess
from collections.abc import Iterable
from pathlib import Path
from sys import platform

from . import Profile
from .launch import launch_qutebrowser
from .utils import env_menus, error, installed_menus, or_phrase


def choose_profile(
    profile_dir: Path, menu: str | None, foreground: bool, qb_args: tuple[str, ...]
) -> bool:
    menu = menu or next(installed_menus(), None)
    if not menu:
        possible_menus = or_phrase([menu for menu in env_menus() if menu != "fzf-tmux"])
        error(
            "no menu program found, use --menu to provide a dmenu-compatible menu or install one of "
            + possible_menus
        )
        return False
    if menu == "applescript" and platform != "darwin":
        error(f"applescript cannot be used on a {platform} host")
        return False
    real_profiles = {profile.name for profile in profile_dir.iterdir()}
    if len(real_profiles) == 0:
        error("no profiles")
        return False
    profiles = [*real_profiles, "qutebrowser"]

    command = menu_command(menu, profiles, qb_args)
    if not command:
        return False

    selection_cmd = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=None,
    )
    out = selection_cmd.stdout
    selection = out and out.read().decode(errors="ignore").rstrip("\n")

    if selection == "qutebrowser" and "qutebrowser" not in real_profiles:
        return launch_qutebrowser(None, foreground, qb_args)
    elif selection:
        profile = Profile(selection, profile_dir)
        return launch_qutebrowser(profile, foreground, qb_args)
    else:
        error("no profile selected")
        return False


def menu_command(
    menu: str, profiles: Iterable[str], qb_args: tuple[str, ...]
) -> str | None:
    profiles = sorted(profiles)
    arg_string = " ".join(qb_args)
    if menu == "applescript":
        profile_list = '", "'.join(profiles)
        return f"""osascript -e \'set profiles to {{"{profile_list}"}}
set profile to choose from list profiles with prompt "qutebrowser: {arg_string}" default items {{item 1 of profiles}}
item 1 of profile\'"""

    prompt = "-p qutebrowser"
    command = menu
    if len(menu.split(" ")) == 1:
        program = Path(menu).name
        if program == "rofi":
            command = f"{menu} -dmenu -no-custom {prompt} -mesg '{arg_string}'"
        elif program == "wofi":
            command = f"{menu} --dmenu {prompt}"
        elif program.startswith("dmenu"):
            command = f"{menu} {prompt}"
        elif program.startswith("fzf"):
            command = f"{menu} --prompt 'qutebrowser '"
        elif program == "fuzzel":
            command = f"{menu} -d"
    exe = command.split(" ")[0]
    if not shutil.which(exe):
        error(f"command '{exe}' not found")
        return None
    profile_list = "\n".join(profiles)
    return f'echo "{profile_list}" | {command}'
