import shutil
import subprocess
from pathlib import Path
from sys import platform
from typing import Optional

from xdg import BaseDirectory

from . import profiles
from .profiles import Profile
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
    profile_dir: Path, menu: str, foreground: bool, qb_args: tuple[str, ...]
) -> bool:
    menu = menu or next(installed_menus())
    if not menu:
        error(f"No menu program found, please install one of: {AUTO_MENUS}")
        return False
    if menu == "applescript" and platform != "darwin":
        error(f"Menu applescript cannot be used on a {platform} host")
        return False
    profiles = [profile.name for profile in sorted(profile_dir.iterdir())]
    if len(profiles) == 0:
        error("No profiles")
        return False

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

    if selection:
        profile = Profile(selection, profile_dir)
        return launch(profile, False, foreground, qb_args)
    else:
        error("No profile selected")
        return False


def menu_command(
    menu: str, profiles: list[str], qb_args: tuple[str, ...]
) -> Optional[str]:
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
