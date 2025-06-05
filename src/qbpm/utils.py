import logging
import platform
from collections.abc import Iterator
from os import environ
from shutil import which

WAYLAND_MENUS = ["fuzzel", "wofi", "dmenu-wl"]
X11_MENUS = ["rofi", "dmenu"]
SUPPORTED_MENUS = [*WAYLAND_MENUS, *X11_MENUS, "fzf", "applescript"]


def info(msg: str) -> None:
    logging.info(msg)


def error(msg: str) -> None:
    logging.error(msg)


def installed_menus() -> Iterator[str]:
    if platform.system() == "Darwin":
        yield "applescript"
    for menu_cmd in env_menus():
        if which(menu_cmd) is not None:
            if menu_cmd == "fzf":
                info("no graphical launchers found, trying fzf")
            yield menu_cmd


def env_menus() -> Iterator[str]:
    if environ.get("WAYLAND_DISPLAY"):
        yield from WAYLAND_MENUS
    elif environ.get("DISPLAY"):
        yield from X11_MENUS
    if environ.get("TMUX"):
        yield "fzf-tmux"
    # if there's no display and fzf is installed we're probably(?) in a term
    if which("fzf") is not None:
        info("no graphical launchers found, trying fzf")
        yield "fzf"


def or_phrase(items: list) -> str:
    strings = list(map(str, items))
    size = len(strings)
    if size == 0:
        return "[]"
    elif size == 1:
        return strings[0]
    elif size == 2:
        return " or ".join(strings)
    else:
        return ", or ".join([", ".join(strings[0:-1]), strings[-1]])
