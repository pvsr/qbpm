import subprocess
from pathlib import Path

from . import Profile
from .launch import launch_qutebrowser
from .log import error
from .menus import find_menu


def choose_profile(
    profile_dir: Path,
    menu: str | list[str],
    prompt: str,
    foreground: bool,
    qb_args: tuple[str, ...],
) -> bool:
    dmenu = find_menu(menu)
    if not dmenu:
        return False

    real_profiles = {profile.name for profile in profile_dir.iterdir()}
    if len(real_profiles) == 0:
        error("no profiles")
        return False
    profiles = [*real_profiles, "qutebrowser"]
    command = dmenu.command(sorted(profiles), prompt, " ".join(qb_args))
    selection_cmd = subprocess.run(
        command,
        text=True,
        input="\n".join(sorted(profiles)),
        stdout=subprocess.PIPE,
        stderr=None,
        check=False,
    )
    out = selection_cmd.stdout
    selection = out.rstrip("\n")

    if selection == "qutebrowser" and "qutebrowser" not in real_profiles:
        return launch_qutebrowser(None, foreground, qb_args)
    elif selection:
        profile = Profile(selection, profile_dir)
        return launch_qutebrowser(profile, foreground, qb_args)
    else:
        error("no profile selected")
        return False
