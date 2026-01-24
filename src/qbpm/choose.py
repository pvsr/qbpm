import subprocess

from . import Profile
from .config import Config
from .launch import launch_qutebrowser
from .log import error
from .menus import find_menu


def choose_profile(
    config: Config,
    foreground: bool,
    qb_args: tuple[str, ...],
) -> bool:
    dmenu = find_menu(config.menu)
    if not dmenu:
        return False

    real_profiles = {profile.name for profile in config.profile_directory.iterdir()}
    if len(real_profiles) == 0:
        error("no profiles")
        return False
    profiles = [*real_profiles]
    include_qb = config.qutebrowser_in_choose and "qutebrowser" not in real_profiles
    if include_qb:
        profiles.append("qutebrowser")
    command = dmenu.command(sorted(profiles), config.menu_prompt, " ".join(qb_args))
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

    if include_qb and selection == "qutebrowser":
        return launch_qutebrowser(None, foreground, qb_args)
    elif selection:
        profile = Profile(selection, config.profile_directory)
        return launch_qutebrowser(profile, foreground, qb_args)
    else:
        error("no profile selected")
        return False
