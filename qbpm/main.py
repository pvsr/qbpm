import argparse
from pathlib import Path
from typing import Callable, Optional

from qbpm import conf, operations, profiles


def main() -> None:
    parser = argparse.ArgumentParser(description="Qutebrowser profile manager")
    parser.add_argument(
        "-P",
        "--profile-dir",
        metavar="directory",
        type=Path,
        help="directory in which profiles are stored",
    )

    subparsers = parser.add_subparsers()
    new = subparsers.add_parser("new")
    new.set_defaults(operation=lambda args: profiles.new_profile(args.profile_name))
    new.add_argument("profile_name", metavar="name", help="name of the new profile")
    creator_args(new)

    session = subparsers.add_parser("from-session")
    session.set_defaults(
        operation=lambda args: operations.from_session(args.session, args.profile_name),
    )
    session.add_argument(
        "session", help="session to create a new profile from",
    )
    session.add_argument(
        "profile_name",
        metavar="name",
        nargs="?",
        help="name of the new profile. if unset the session name will be used",
    )
    creator_args(session)

    launch = subparsers.add_parser("launch", aliases=["run"])
    launch.set_defaults(
        operations=lambda args: operations.launch(
            args.profile_name, args.strict, args.foreground
        )
    )
    launch.add_argument(
        "profile_name",
        metavar="name",
        nargs="?",
        help="profile to launch. it will be created if it does not exist, unless -s is set",
    )
    launch.add_argument(
        "-s",
        "--strict",
        action="store_true",
        help="return an error if the profile does not exist",
    )
    launch.add_argument(
        "-f",
        "--foreground",
        action="store_true",
        help="launch qutebrowser in the foreground and print its stdout and stderr to the console",
    )

    args = parser.parse_args()
    if args.profile_dir:
        conf.profiles_dir = args.profile_dir
    args.operation(args)


def creator_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-l",
        "--launch",
        action=ThenLaunchAction,
        dest="operation",
        help="name of the new profile. if unset the session name will be used",
    )
    parser.set_defaults(
        strict=True, foreground=False,
    )


class ThenLaunchAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        super(ThenLaunchAction, self).__init__(
            option_strings, dest, nargs=nargs, **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        operation = getattr(namespace, self.dest)
        if operation:
            composed = lambda args: then_launch(args, operation)
            setattr(namespace, self.dest, composed)


def then_launch(
    args: argparse.Namespace, operation: Callable[[argparse.Namespace], Optional[Path]]
) -> bool:
    profile = operation(args)
    if profile:
        return operations.launch(profile, args.strict, args.foreground)
    return False
