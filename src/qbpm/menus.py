import platform
import sys
from collections.abc import Iterator
from dataclasses import dataclass, replace
from os import environ
from pathlib import Path
from shutil import which

from .log import error, or_phrase


@dataclass
class Dmenu:
    name: str
    args: str

    def installed(self) -> bool:
        return which(self.name) is not None

    def command(self, prompt: str, qb_args: str) -> str:
        return f"{self.name} {self.args.format(prompt=prompt, qb_args=qb_args)}"

    def commandline(self, profiles: list[str], prompt: str, qb_args: str) -> str:
        profile_list = "\n".join(profiles)
        return f'echo "{profile_list}" | {self.command(prompt, qb_args)}'


class ApplescriptMenu:
    @classmethod
    def installed(cls) -> bool:
        return platform.system() == "Darwin"

    @classmethod
    def commandline(cls, profiles: list[str], _prompt: str, qb_args: str) -> str:
        profile_list = '", "'.join(profiles)
        return f"""osascript -e \'set profiles to {{"{profile_list}"}}
set profile to choose from list profiles with prompt "qutebrowser: {qb_args}" default items {{item 1 of profiles}}
item 1 of profile\'"""


def find_menu(menu: str | None) -> Dmenu | ApplescriptMenu | None:
    menus = list(supported_menus())
    if not menu:
        found = next(filter(lambda m: m.installed(), menus), None)
        if not found:
            error(
                "no menu program found, use --menu to provide a dmenu-compatible menu or install one of "
                + or_phrase([m.name for m in menus if isinstance(m, Dmenu)])
            )
        return found
    dmenu = custom_dmenu(menu)
    if not dmenu.installed():
        error(f"{dmenu.name} not found")
        return None
    return dmenu


def custom_dmenu(command: str) -> Dmenu:
    split = command.split(" ", maxsplit=1)
    if len(split) == 1 or not split[1]:
        name = Path(command).name
        for m in supported_menus():
            if isinstance(m, Dmenu) and m.name == name:
                return m if m.name == command else replace(m, name=command)
    return Dmenu(split[0], split[1] if len(split) == 2 else "")


def supported_menus() -> Iterator[Dmenu | ApplescriptMenu]:
    if ApplescriptMenu.installed():
        yield ApplescriptMenu()
    if environ.get("WAYLAND_DISPLAY"):
        yield from [
            # default window is too narrow for a long prompt
            Dmenu("fuzzel", "--dmenu"),
            Dmenu("wofi", "--dmenu -p {prompt}"),
            Dmenu("dmenu-wl", "-p {prompt}"),
        ]
    if environ.get("DISPLAY"):
        yield from [
            Dmenu(
                "rofi",
                "-dmenu -no-custom -p {prompt} -mesg '{qb_args}'",
            ),
            Dmenu("dmenu", "-p {prompt}"),
        ]
    if sys.stdin.isatty():
        if environ.get("TMUX"):
            yield Dmenu("fzf-tmux", "--prompt {prompt}")
        yield Dmenu("fzf", "--prompt {prompt}")
