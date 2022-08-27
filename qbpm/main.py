import argparse
import inspect
from os import environ
from pathlib import Path
from typing import Any, Callable, Optional

from xdg import BaseDirectory

from . import __version__, operations, profiles
from .profiles import Profile
from .utils import SUPPORTED_MENUS, error

DEFAULT_PROFILE_DIR = Path(BaseDirectory.xdg_data_home) / "qutebrowser-profiles"


def main(mock_args: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="qutebrowser profile manager")
    parser.set_defaults(
        operation=lambda args: parser.print_help(), passthrough=False, launch=False
    )
    parser.add_argument(
        "-P",
        "--profile-dir",
        metavar="directory",
        type=Path,
        help="directory in which profiles are stored",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
    )

    subparsers = parser.add_subparsers()
    new = subparsers.add_parser("new", help="create a new profile")
    new.add_argument("profile_name", metavar="profile", help="name of the new profile")
    new.add_argument("home_page", metavar="url", nargs="?", help="profile's home page")
    new.set_defaults(operation=build_op(profiles.new_profile))
    creator_args(new)

    session = subparsers.add_parser(
        "from-session", help="create a new profile from a qutebrowser session"
    )
    session.add_argument(
        "session",
        help="path to session file or name of session. "
        "e.g. ~/.local/share/qutebrowser/sessions/example.yml or example",
    )
    session.add_argument(
        "profile_name",
        metavar="profile",
        nargs="?",
        help="name of the new profile. if unset the session name will be used",
    )
    session.set_defaults(operation=build_op(operations.from_session))
    creator_args(session)

    desktop = subparsers.add_parser(
        "desktop", help="create a desktop file for an existing profile"
    )
    desktop.add_argument(
        "profile_name", metavar="profile", help="profile to create a desktop file for"
    )
    desktop.set_defaults(operation=build_op(operations.desktop))

    launch = subparsers.add_parser(
        "launch", help="launch qutebrowser with the given profile"
    )
    launch.add_argument(
        "profile_name",
        metavar="profile",
        help="profile to launch. it will be created if it does not exist, unless -s is set",
    )
    launch.add_argument(
        "-n",
        "--new",
        action="store_false",
        dest="strict",
        help="create the profile if it doesn't exist",
    )
    launch.add_argument(
        "-f",
        "--foreground",
        action="store_true",
        help="launch qutebrowser in the foreground and print its stdout and stderr to the console",
    )
    launch.set_defaults(operation=build_op(operations.launch), passthrough=True)

    list_ = subparsers.add_parser("list", help="list existing profiles")
    list_.set_defaults(operation=operations.list_)

    choose = subparsers.add_parser(
        "choose",
        help="interactively choose a profile to launch",
    )
    menus = sorted(SUPPORTED_MENUS)
    choose.add_argument(
        "-m",
        "--menu",
        help=f'menu application to use. this may be any dmenu-compatible command (e.g. "dmenu -i -p qbpm" or "/path/to/rofi -d") or one of the following menus with built-in support: {menus}',
    )
    choose.add_argument(
        "-f",
        "--foreground",
        action="store_true",
        help="launch qutebrowser in the foreground and print its stdout and stderr to the console",
    )
    choose.set_defaults(operation=operations.choose, passthrough=True)

    edit = subparsers.add_parser("edit", help="edit a profile's config.py")
    edit.add_argument("profile_name", metavar="profile", help="profile to edit")
    edit.set_defaults(operation=build_op(operations.edit))

    raw_args = parser.parse_known_args(mock_args)
    args = raw_args[0]
    if args.passthrough:
        args.qb_args = raw_args[1]
    elif len(raw_args[1]) > 0:
        error(f"unrecognized arguments: {' '.join(raw_args[1])}")
        exit(1)

    if not args.profile_dir:
        args.profile_dir = Path(environ.get("QBPM_PROFILE_DIR") or DEFAULT_PROFILE_DIR)

    result = args.operation(args)
    if args.launch and result:
        profile = result if isinstance(result, Profile) else Profile.of(args)
        result = operations.launch(
            profile, False, args.foreground, getattr(args, "qb_args", [])
        )
    if not result:
        exit(1)


def creator_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-l",
        "--launch",
        action="store_true",
        help="launch the profile after creating",
    )
    parser.add_argument(
        "-f",
        "--foreground",
        action="store_true",
        help="if --launch is set, launch qutebrowser in the foreground",
    )
    parser.add_argument(
        "--no-desktop-file",
        dest="desktop_file",
        action="store_false",
        help="do not generate a desktop file for the profile",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace existing profile config",
    )
    parser.set_defaults(strict=True)


def build_op(operation: Callable[..., Any]) -> Callable[[argparse.Namespace], Any]:
    def op(args: argparse.Namespace) -> Any:
        params = [
            param.name
            for param in inspect.signature(operation).parameters.values()
            if param.kind == param.POSITIONAL_OR_KEYWORD
        ]
        kwargs = {param: getattr(args, param, None) for param in params}
        if "profile" in params:
            kwargs["profile"] = Profile.of(args)
        return operation(**kwargs)

    return op


if __name__ == "__main__":
    main()
