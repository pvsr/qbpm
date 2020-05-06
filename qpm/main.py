import argparse
from argparse import Namespace
from pathlib import Path
from typing import Callable, Optional, Set

from qpm import operations, profiles
from qpm.profiles import Profile


def main() -> None:
    parser = argparse.ArgumentParser(description="qutebrowser profile manager")
    parser.set_defaults(operation=parser.print_help)
    parser.add_argument(
        "-P",
        "--profile-dir",
        metavar="directory",
        type=Path,
        help="directory in which profiles are stored",
    )

    subparsers = parser.add_subparsers()
    new = subparsers.add_parser("new", help="create a new profile")
    new.set_defaults(operation=wrap_op(profiles.new_profile, set()))
    new.add_argument("profile_name", metavar="name", help="name of the new profile")
    creator_args(new)

    session = subparsers.add_parser(
        "from-session", help="create a new profile from a qutebrowser session"
    )
    session.set_defaults(operation=lambda args: operations.from_session(**vars(args)))
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

    launch = subparsers.add_parser(
        "launch", aliases=["run"], help="launch qutebrowser with the given profile"
    )
    launch.set_defaults(
        operation=wrap_op(operations.launch, {"strict", "foreground", "qb_args"})
    )
    launch.add_argument(
        "profile_name",
        metavar="name",
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

    list_ = subparsers.add_parser("list", help="list existing qutebrowser profiles")
    list_.set_defaults(operation=lambda args: operations.list_())

    raw_args = parser.parse_known_args()
    args = raw_args[0]
    args.qb_args = raw_args[1]
    args.operation(args)


def creator_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-l",
        "--launch",
        action=ThenLaunchAction,
        dest="operation",
        help="launch the profile after creating",
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
    args: argparse.Namespace,
    operation: Callable[[argparse.Namespace], Optional[Profile]],
) -> bool:
    profile = operation(args)
    if profile:
        return operations.launch(profile, args.strict, args.foreground, [])
    return False


def wrap_op(
    op: Callable[..., bool], wanted: Set[str]
) -> Callable[[Namespace], Optional[Profile]]:
    def f(args) -> Optional[Profile]:
        profile = Profile(args.profile_name, args.profile_dir)
        kwargs = {k: v for (k, v) in vars(args).items() if k in wanted}
        return profile if op(profile=profile, **kwargs) else None

    return f


if __name__ == "__main__":
    main()
