import argparse
import os
import shutil
import subprocess
from pathlib import Path
from sys import platform
from typing import List, Optional

from xdg import BaseDirectory  # type: ignore
from xdg.DesktopEntry import DesktopEntry  # type: ignore

from qpm import profiles
from qpm.profiles import Profile
from qpm.utils import error, get_default_menu, user_data_dir


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
    if not args.menu:
        args.menu = "dmenu" if args.dmenu else get_default_menu()
        if not args.menu:
            error("No suitable menu program found, please install rofi or dmenu")
            return None
    elif args.menu not in ["rofi", "dmenu", "applescript"]:
        error(
            f"{args.menu} is not a valid menu program, please specify one of rofi, dmenu, or applescript"
        )
        return None
    elif args.menu == "applescript" and platform != "darwin":
        error(f"Menu applescript cannot be used on a {platform} host")
        return None
    elif args.dmenu:
        args.menu = "dmenu"
    elif shutil.which(args.menu) is None:
        error(f"{args.menu} not found on path")
        return None

    profile_list = "\n".join(
        [profile.name for profile in sorted(args.profile_dir.iterdir())]
    )
    if not profile_list:
        error("No existing profiles found, create a profile first with qbpm new")
        return None

    if args.menu == "rofi":
        arg_string = " ".join(args.qb_args)
        cmd_string = f'echo "{profile_list}" | rofi -dmenu -no-custom -p qutebrowser -mesg {arg_string}'
    elif args.menu in ["dmenu", "dmenu-wl"]:
        dmenu_command = args.dmenu or f"{args.menu} -p qutebrowser"
        cmd_string = f'echo "{profile_list}" | {dmenu_command}'
    elif args.menu == "applescript":
        profile_list = '", "'.join(profile_list.split("\n"))
        arg_string = " ".join(args.qb_args)
        cmd_string = f"""osascript -e \'set profiles to {{"{profile_list}"}}
set profile to choose from list profiles with prompt "qutebrowser: {arg_string}" default items {{item 1 of profiles}}
item 1 of profile\'"""

    selection_cmd = subprocess.Popen(
        cmd_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    out = selection_cmd.stdout
    if not out:
        error(f"Could not read {args.menu} stdout")
        return None
    selection = out.read().decode(errors="ignore").rstrip("\n")

    if selection:
        profile = Profile(selection, args.profile_dir, args.set_app_id)
        launch(profile, True, args.foreground, args.qb_args)
    else:
        error("No profile selected")


def edit(profile: Profile):
    if not profile.exists():
        error(f"profile {profile.name} not found at {profile.root}")
        return
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vim"
    os.execlp(editor, editor, str(profile.root / "config" / "config.py"))
