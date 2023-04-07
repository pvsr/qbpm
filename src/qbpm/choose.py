import subprocess
from pathlib import Path

from . import Profile
from .launch import launch_qutebrowser
from .icons import icon_for_profile
from .log import error
from .menus import find_menu


# TODO take config arg
def choose_profile(
    profile_dir: Path,
    menu: str | list[str],
    prompt: str,
    foreground: bool,
    qb_args: tuple[str, ...],
    force_icon: bool = False,
) -> bool:
    dmenu = find_menu(menu)
    if not dmenu:
        return False

    real_profiles = {profile.name for profile in profile_dir.iterdir()}
    if len(real_profiles) == 0:
        error("no profiles")
        return False
    profiles = [*real_profiles, "qutebrowser"]
    use_icon = force_icon
    # TODO check config
    # TODO get menu icon support
    # use_icon = dmenu.icon_support or force_icon
    command = dmenu.command(sorted(profiles), prompt, " ".join(qb_args))
    selection_cmd = subprocess.run(
        command,
        text=True,
        input=build_menu_items(profiles, use_icon),
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


def build_menu_items(profiles: list[str], icon: bool) -> str:
    # TODO build profile before passing to icons
    if icon and any(profile_icons := [icon_for_profile(p) for p in profiles]):
        menu_items = [
            icon_entry(profile, icon)
            for (profile, icon) in zip(profiles, profile_icons)
        ]
    else:
        menu_items = profiles

    return "\n".join(sorted(menu_items))


def icon_entry(name: str, icon: str | None) -> str:
    return f"{name}\0icon\x1f{icon or 'qutebrowser'}"
