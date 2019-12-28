from argparse import ArgumentParser

from qbpm import operations, profiles


def main():
    parser = ArgumentParser(description="Qutebrowser profile manager")

    subparsers = parser.add_subparsers()
    new = subparsers.add_parser("new")
    new.add_argument("profile_name", metavar="name", help="name of the new profile")
    new.set_defaults(operation=lambda args: profiles.new_profile(args.profile_name))

    session = subparsers.add_parser("from-session")
    session.add_argument(
        "session", help="session to create a new profile from",
    )
    session.add_argument(
        "profile_name",
        metavar="name",
        nargs="?",
        help="name of the new profile. if unset the session name will be used",
    )
    session.set_defaults(
        operation=lambda args: operations.from_session(args.session, args.profile_name)
    )

    launch = subparsers.add_parser("launch", aliases=["run"])
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
    launch.set_defaults(
        operation=lambda args: operations.launch(
            args.profile_name, args.strict, args.foreground
        )
    )

    args = parser.parse_args()
    args.operation(args)
