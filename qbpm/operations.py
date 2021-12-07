import argparse
import os
import shutil
import subprocess
from pathlib import Path
from sys import platform, stderr
from typing import List, Optional

from xdg import BaseDirectory  # type: ignore
from xdg.DesktopEntry import DesktopEntry  # type: ignore

from qbpm import profiles
from qbpm.profiles import Profile
from qbpm.utils import SUPPORTED_MENUS, error, get_default_menu, user_data_dir


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
    profile: Profile, strict: bool, foreground: bool, qb_args: List[str]
) -> bool:
    if not profiles.ensure_profile_exists(profile, not strict):
        return False

    args = profile.cmdline() + qb_args
    if foreground:
        os.execlp("qutebrowser", *args)
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


def desktop(profile: Profile):
    if profile.exists():
        profiles.create_desktop_file(profile)
    else:
        error(f"profile {profile.name} not found at {profile.root}")


def list_(args: argparse.Namespace) -> None:
    for profile in sorted(args.profile_dir.iterdir()):
        print(profile.name)


def choose(args: argparse.Namespace) -> None:
    menu = args.menu or get_default_menu()
    if not menu:
        error(
            "No suitable menu program found, please install one of: {SUPPORTED_MENUS}"
        )
        return None
    if menu == "applescript" and platform != "darwin":
        error(f"Menu applescript cannot be used on a {platform} host")
        return None
    if len(menu.split(" ")) == 1 and not shutil.which(menu):
        error(f"'{menu}' not found on path")
        return None

    profiles = [profile.name for profile in sorted(args.profile_dir.iterdir())]
    if len(profiles) == 0:
        error("No profiles")
        return None

    command = menu_command(menu, profiles, args)
    selection_cmd = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out = selection_cmd.stdout
    if not out:
        error(f"Could not read stdout from {command}")
        return None
    selection = out.read().decode(errors="ignore").rstrip("\n")

    if selection:
        profile = Profile(selection, args.profile_dir, args.set_app_id)
        launch(profile, True, args.foreground, args.qb_args)
    else:
        error("No profile selected")
        if err := selection_cmd.stderr:
            msg = err.read().decode(errors="ignore").rstrip("\n")
            if msg:
                for line in msg.split("\n"):
                    print(f"stderr: {line}", file=stderr)


def menu_command(menu: str, profiles, args: argparse.Namespace) -> str:
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
        elif program in ["dmenu", "dmenu-wl"]:
            command = f"{menu} {prompt}"
    profile_list = "\n".join(profiles)
    return f'echo "{profile_list}" | {command}'


def edit(profile: Profile):
    if not profile.exists():
        error(f"profile {profile.name} not found at {profile.root}")
        return
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vim"
    os.execlp(editor, editor, str(profile.root / "config" / "config.py"))
