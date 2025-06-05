import shutil
import subprocess
from collections.abc import Iterable
from pathlib import Path
from sys import platform

from . import Profile, profiles
from .desktop import create_desktop_file
from .utils import env_menus, error, installed_menus, or_phrase, qutebrowser_exe


def from_session(
    profile: Profile,
    session_path: Path,
    qb_config_dir: Path | None,
    desktop_file: bool = True,
    overwrite: bool = False,
) -> bool:
    if not profiles.new_profile(profile, qb_config_dir, None, desktop_file, overwrite):
        return False

    session_dir = profile.root / "data" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=overwrite)
    shutil.copy(session_path, session_dir / "_autosave.yml")

    return True


def launch(profile: Profile, foreground: bool, qb_args: tuple[str, ...]) -> bool:
    if not profiles.exists(profile):
        return False

    args = profile.cmdline() + list(qb_args)
    return launch_internal(foreground, args)


def launch_qutebrowser(foreground: bool, qb_args: tuple[str, ...]) -> bool:
    return launch_internal(foreground, [qutebrowser_exe(), *qb_args])


def launch_internal(foreground: bool, args: list[str]) -> bool:
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


def desktop(profile: Profile) -> bool:
    exists = profile.exists()
    if exists:
        create_desktop_file(profile)
    else:
        error(f"profile {profile.name} not found at {profile.root}")
    return exists


def choose(
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
        return launch_qutebrowser(foreground, qb_args)
    elif selection:
        profile = Profile(selection, profile_dir)
        return launch(profile, foreground, qb_args)
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
