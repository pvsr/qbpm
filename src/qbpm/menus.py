import platform
import shlex
import sys
from collections.abc import Iterator
from dataclasses import dataclass, replace
from os import environ
from pathlib import Path
from shutil import which

from .log import error, or_phrase


@dataclass(frozen=True)
class Dmenu:
    menu_command: list[str]

    def name(self) -> str:
        return self.menu_command[0]

    def installed(self) -> bool:
        return which(self.name()) is not None

    def command(self, _profiles: list[str], prompt: str, qb_args: str) -> list[str]:
        prompt = prompt.format(qb_args=qb_args)
        return [arg.format(prompt=prompt, qb_args=qb_args) for arg in self.menu_command]


class ApplescriptMenu:
    @classmethod
    def name(cls) -> str:
        return "applescript"

    @classmethod
    def installed(cls) -> bool:
        return platform.system() == "Darwin"

    @classmethod
    def command(cls, profiles: list[str], _prompt: str, qb_args: str) -> list[str]:
        profile_list = '", "'.join(profiles)
        return [
            "osascript",
            "-e",
            f"""set profiles to {{"{profile_list}"}}
set profile to choose from list profiles with prompt "qutebrowser: {qb_args}" default items {{item 1 of profiles}}
item 1 of profile""",
        ]


def find_menu(menu: str | list[str] | None) -> Dmenu | ApplescriptMenu | None:
    if menu:
        dmenu = custom_dmenu(menu)
        if not dmenu.installed():
            error(f"{dmenu.name()} not found")
            return None
        return dmenu
    menus = list(supported_menus())
    found = next(filter(lambda m: m.installed(), menus), None)
    if not found:
        error(
            "no menu program found, use --menu to provide a dmenu-compatible menu or install one of "
            + or_phrase([m.name() for m in menus if isinstance(m, Dmenu)])
        )
    return found


def custom_dmenu(command: str | list[str]) -> Dmenu:
    split = shlex.split(command) if isinstance(command, str) else command
    if len(split) == 1 or not split[1]:
        command_path = Path(split[0])
        name = command_path.name
        for menu in supported_menus():
            if isinstance(menu, Dmenu) and menu.name() == name:
                return (
                    menu
                    if name == split[0]
                    else replace(
                        menu,
                        menu_command=[
                            str(command_path.expanduser()),
                            *menu.menu_command[1::],
                        ],
                    )
                )
    return Dmenu(split)


def supported_menus() -> Iterator[Dmenu | ApplescriptMenu]:
    if ApplescriptMenu.installed():
        yield ApplescriptMenu()
    if environ.get("WAYLAND_DISPLAY"):
        yield from [
            # default window is too narrow for a long prompt
            Dmenu(["fuzzel", "--dmenu"]),
            Dmenu(["walker", "--dmenu", "--placeholder", "{prompt}"]),
            Dmenu(["wofi", "--dmenu", "--prompt", "{prompt}"]),
            Dmenu(["tofi", "--prompt-text", "{prompt}> "]),
            Dmenu(["wmenu", "-p", "{prompt}"]),
            Dmenu(["dmenu-wl", "--prompt", "{prompt}"]),
        ]
    if environ.get("DISPLAY"):
        yield from [
            Dmenu(
                [
                    "rofi",
                    "-dmenu",
                    "-no-custom",
                    "-p",
                    "{prompt}",
                    "-mesg",
                    "{qb_args}",
                ]
            ),
            Dmenu(["dmenu", "-p", "{prompt}"]),
        ]
    if sys.stdin.isatty():
        if environ.get("TMUX"):
            yield Dmenu(["fzf-tmux", "--prompt", "{prompt}> "])
        yield Dmenu(["fzf", "--prompt", "{prompt}> "])
