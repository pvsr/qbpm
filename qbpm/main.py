from argparse import ArgumentParser

from qbpm import operations


def main():
    parser = ArgumentParser(description="Qutebrowser profile manager")

    subparsers = parser.add_subparsers()
    new = subparsers.add_parser("new")
    new.add_argument("profile_name", metavar="name", help="name of the new profile")
    new.set_defaults(operation=lambda args: operations.new_profile(args.profile_name))

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

    args = parser.parse_args()
    args.operation(args)
