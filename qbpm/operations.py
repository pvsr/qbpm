import argparse
import os
import shutil
import subprocess
from pathlib import Path
from sys import platform
from typing import Optional

from xdg import BaseDirectory

from . import profiles
from .profiles import Profile
from .utils import AUTO_MENUS, error, installed_menus, user_data_dir


def from_session(
    session: str,
    profile_name: Optional[str] = None,
    profile_dir: Optional[Path] = None,
    desktop_file: bool = True,
    overwrite: bool = False,
) -> Optional[Profile]:
    if session.endswith(".yml"):
        session_file = Path(session).expanduser()
        session_name = session_file.stem
    else:
        session_name = session
        session_file = user_data_dir() / "sessions" / (session_name + ".yml")
    if not session_file.is_file():
        error(f"{session_file} is not a file")
        return None

    profile = Profile(profile_name or session_name, profile_dir)
    if not profiles.new_profile(profile, None, desktop_file, overwrite):
        return None

    session_dir = profile.root / "data" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=overwrite)
    shutil.copy(session_file, session_dir / "_autosave.yml")

    return profile


def launch(
    profile: Profile, strict: bool, foreground: bool, qb_args: list[str]
) -> bool:
    if not profiles.ensure_profile_exists(profile, not strict):
        return False

    args = profile.cmdline() + qb_args
    if not shutil.which(args[0]):
        error("qutebrowser is not installed")
        return False

    if foreground:
        return subprocess.run(args).returncode == 0
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


def list_(args: argparse.Namespace) -> bool:
    for profile in sorted(args.profile_dir.iterdir()):
        print(profile.name)
    return True


def choose(args: argparse.Namespace) -> bool:
    menu = args.menu or next(installed_menus())
    if not menu:
        error(f"No menu program found, please install one of: {AUTO_MENUS}")
        return False
    if menu == "applescript" and platform != "darwin":
        error(f"Menu applescript cannot be used on a {platform} host")
        return False
    profiles = [profile.name for profile in sorted(args.profile_dir.iterdir())]
    if len(profiles) == 0:
        error("No profiles")
        return False

    command = menu_command(menu, profiles, args)
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
        profile = Profile(selection, args.profile_dir)
        launch(profile, True, args.foreground, args.qb_args)
    else:
        error("No profile selected")
        return False
    return True


def menu_command(
    menu: str, profiles: list[str], args: argparse.Namespace
) -> Optional[str]:
    arg_string = " ".join(args.qb_args)
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
            command = f"{menu} -dmenu -no-custom {prompt} -mesg {arg_string}"
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


def edit(profile: Profile) -> bool:
    if not profile.exists():
        error(f"profile {profile.name} not found at {profile.root}")
        return False
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vim"
    os.execlp(editor, editor, str(profile.root / "config" / "config.py"))
    return True
