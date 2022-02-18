import argparse
from os import environ
from pathlib import Path
from typing import Any, Callable, Optional

from xdg import BaseDirectory  # type: ignore

from qbpm import __version__, operations, profiles
from qbpm.profiles import Profile
from qbpm.utils import SUPPORTED_MENUS, error

DEFAULT_PROFILE_DIR = Path(BaseDirectory.xdg_data_home) / "qutebrowser-profiles"


def main(mock_args=None) -> None:
    parser = argparse.ArgumentParser(description="qutebrowser profile manager")
    parser.set_defaults(operation=lambda args: parser.print_help(), passthrough=False)
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
    new.set_defaults(
        operation=lambda args: profiles.new_profile(
            Profile.of(args),
            args.home_page,
            args.desktop_file,
            args.overwrite,
        )
    )
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
    session.set_defaults(
        operation=lambda args: operations.from_session(
            args.session,
            args.profile_name,
            args.profile_dir,
            args.desktop_file,
            args.overwrite,
        )
    )
    creator_args(session)

    desktop = subparsers.add_parser(
        "desktop", help="create a desktop file for an existing profile"
    )
    desktop.add_argument(
        "profile_name", metavar="profile", help="profile to create a desktop file for"
    )
    desktop.set_defaults(operation=lambda args: operations.desktop(Profile.of(args)))

    launch = subparsers.add_parser(
        "launch", aliases=["run"], help="launch qutebrowser with the given profile"
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
    launch.set_defaults(
        operation=lambda args: operations.launch(
            Profile.of(args), args.strict, args.foreground, args.qb_args
        ),
        passthrough=True,
    )

    list_ = subparsers.add_parser("list", help="list existing profiles")
    list_.set_defaults(operation=operations.list_)

    choose = subparsers.add_parser(
        "choose",
        help="choose profile using a dmenu-compatible launcher or an applescript dialog",
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

    edit = subparsers.add_parser(
        "edit", help="edit a profile's config.py using $EDITOR"
    )
    edit.add_argument("profile_name", metavar="profile", help="profile to edit")
    edit.set_defaults(operation=lambda args: operations.edit(Profile.of(args)))

    raw_args = parser.parse_known_args(mock_args)
    args = raw_args[0]
    if args.passthrough:
        args.qb_args = raw_args[1]
    elif len(raw_args[1]) > 0:
        error(f"unrecognized arguments: {' '.join(raw_args[1])}")
        exit(1)

    if not args.profile_dir:
        args.profile_dir = Path(environ.get("QBPM_PROFILE_DIR") or DEFAULT_PROFILE_DIR)
    if not args.operation(args):
        exit(1)


def creator_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-l",
        "--launch",
        action=ThenLaunchAction,
        dest="operation",
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


class ThenLaunchAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        super(ThenLaunchAction, self).__init__(
            option_strings, dest, nargs=nargs, **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        if operation := getattr(namespace, self.dest):
            setattr(namespace, self.dest, lambda args: then_launch(args, operation))


def then_launch(
    args: argparse.Namespace,
    operation: Callable[[argparse.Namespace], Optional[Any]],
) -> bool:
    if result := operation(args):
        if isinstance(result, Profile):
            profile = result
        else:
            profile = Profile.of(args)
        return operations.launch(profile, False, args.foreground, args.qb_args)
    return False


if __name__ == "__main__":
    main()
