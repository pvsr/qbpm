import sys
import argparse
from pathlib import Path
from typing import Optional

from jinja2 import (
    ChoiceLoader,
    Environment,
    DictLoader,
    FileSystemLoader,
    TemplateNotFound,
)
from xdg import BaseDirectory
from xdg.DesktopEntry import DesktopEntry

CUSTOM_TEMPLATES = {}

ENV = Environment(
    loader=ChoiceLoader([DictLoader(CUSTOM_TEMPLATES), FileSystemLoader("templates")]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render(name: str) -> Optional[str]:
    try:
        return ENV.get_template(name).render()
    except TemplateNotFound as ex:
        print("Template not found:", ex)
        return None


def dash_case(string: str) -> str:
    return string.lower().replace(" ", "-").replace("_", "-")


def parse():
    # TODO argparse for:
    ## Desktop info: generic name, types, keywords
    ## arbitrary qutebrowser options for ssb.py?
    parser = argparse.ArgumentParser(description="program desc")

    parser.add_argument(
        "name",
        help="user-friendly name of your qutebrowser profile, e.g. 'Python' or 'My Cool Webapp'",
    )

    # TODO get default from config file?
    parser.add_argument(
        "-p",
        "--profile-location",
        metavar="DIR",
        type=Path,
        default=Path(BaseDirectory.save_data_path("qute-profiles")),
        help="location of qute-profile configurations. defaults to $XDG_DATA_HOME/qute-profiles",
    )

    prefix = parser.add_mutually_exclusive_group()
    prefix.add_argument(
        "--prefix",
        metavar="DIR",
        nargs="?",
        default="qute-profiles",
        help="group qute-profile binaries and desktop files in a directory called DIR."
        + " defaults to 'qute-profiles'",
    )
    prefix.add_argument(
        "--no-prefix",
        dest="prefix",
        action="store_const",
        const=None,
        help="disable prefix directory",
    )

    binary = parser.add_mutually_exclusive_group()
    binary.add_argument(
        "-b",
        "--bin",
        metavar="DIR",
        type=Path,
        default=Path.home() / "bin",
        help="directory to store binaries in. defaults to $HOME/bin",
    )
    binary.add_argument(
        "--no-bin",
        dest="bin",
        action="store_const",
        const=None,
        help="disable binary generation",
    )

    parser.add_argument(
        "-D",
        "--no-desktop",
        dest="desktop",
        action="store_const",
        const=None,
        default=Path(BaseDirectory.save_data_path("applications")),
        help="disable desktop file generation",
    )

    profile = parser.add_mutually_exclusive_group()
    profile.add_argument(
        "-s",
        "--ssb",
        action="store_true",
        help="use built-in site-specific browser profile",
    )
    profile.add_argument(
        "-c",
        "--custom-profile",
        type=argparse.FileType("r"),
        help="use custom qutebrowser configuration file",
    )

    parser.add_argument(
        "-C",
        "--custom-profile-location",
        metavar="DIR",
        type=Path,
        default=Path(),
        help="location of custom profile, relative to base config dir",
    )

    parser.add_argument(
        "--qb-config-dir",
        metavar="DIR",
        type=Path,
        default=Path(BaseDirectory.save_config_path("qutebrowser")),
        help="source qutebrowser config dir. defaults to $XDG_CONFIG_HOME/qutebrowser",
    )

    parser.add_argument(
        "--qb-data-dir",
        metavar="DIR",
        type=Path,
        default=Path(BaseDirectory.save_data_path("qutebrowser")),
        help="source qutebrowser data dir, defaults to $XDG_DATA_HOME/qutebrowser",
    )

    conf = parser.add_mutually_exclusive_group()
    conf.add_argument(
        "--link-to-config",
        dest="config",
        action="store_const",
        const="symlink",
        help="symlink original config.py/autoconfig.yml to new profile. default operation",
    )
    conf.add_argument(
        "--copy-config",
        dest="config",
        action="store_const",
        const="copy",
        help="copy original config.py/autoconfig.yml to new profile",
    )
    conf.add_argument(
        "--no-copy-config",
        dest="config",
        action="store_const",
        const=None,
        help="do not copy or link config.py/autoconfig.yml",
    )

    parser.add_argument(
        "--copy-history",
        dest="history",
        action="store_const",
        const="copy",
        help="copy original history database to new profile",
    )

    bookmarks = parser.add_mutually_exclusive_group()
    bookmarks.add_argument(
        "--link-to-bookmarks",
        dest="bookmarks",
        action="store_const",
        const="symlink",
        help="symlink original bookmarks and quickmarks to new profile",
    )
    bookmarks.add_argument(
        "--copy-bookmarks",
        dest="bookmarks",
        action="store_const",
        const="copy",
        help="copy original bookmarks and quickmarks to new profile",
    )

    parser.add_argument(
        "-u", "--home-page", nargs="+", help="pages to show when starting profile"
    )

    # TODO
    parser.add_argument(
        "-n", "--dry-run", action="store_true", help="NOT IMPLEMENTED YET"
    )

    # TODO debug option

    return parser.parse_args()


def main() -> None:
    args = parse()

    if args.prefix:
        # apply prefix to desktop and bin dirs if enabled
        args.desktop = args.desktop and args.desktop / args.prefix
        args.bin = args.bin and args.bin / args.prefix

    ENV.globals = {"urls": args.home_page}

    dest_root = args.profile_location / dash_case(args.name)
    if dest_root.exists():
        print("Error: {} already exists".format(dest_root), file=sys.stderr)
        sys.exit(1)

    bin_content = 'qutebrowser --basedir "{basedir}/{name}"'.format(
        basedir=args.profile_location, name=dash_case(args.name)
    )

    config_root = dest_root / "config"

    clone(args.config, args.qb_config_dir, config_root, Path("config.py"))
    clone(args.config, args.qb_config_dir, config_root, Path("autoconfig.yml"))

    clone(args.bookmarks, args.qb_config_dir, config_root, Path("bookmarks/urls"))
    clone(args.bookmarks, args.qb_config_dir, config_root, Path("quickmarks"))

    data_root = dest_root / "config"
    clone(args.history, args.qb_data_dir, data_root, Path("history.sqlite"))

    if args.ssb:
        profile = config_root / args.custom_profile_location / "profile.py"
        profile.parent.mkdir(parents=True, exist_ok=True)
        contents = render("profile.py")
        if contents:
            profile.write_text(contents)
        else:
            # TODO
            print("could not find ssb template", file=sys.stderr)
            sys.exit(1)
    elif args.custom_profile:
        profile = config_root / args.custom_profile_location / "profile.py"
        profile.parent.mkdir(parents=True, exist_ok=True)
        # TODO treat custom prof as template
        profile.write_text(args.custom_profile.read())

    if args.desktop:
        generate_desktop_file(args.desktop, args.name, bin_content)


# TODO return false if failed
def clone(method: str, src_root: Path, dest_root: Path, rel: Path) -> bool:
    src = src_root / rel
    dest = dest_root / rel
    if not method:
        return True
    if method == "symlink":
        return symlink(src, dest)
    if method == "copy":
        return copy(src, dest)

    print("should be unreachable", file=sys.stderr)
    sys.exit(1)


def symlink(src: Path, dest: Path) -> bool:
    dest.write_bytes(src.read_bytes())
    return True


def copy(src: Path, dest: Path) -> bool:
    dest.write_bytes(src.read_bytes())
    return True


def generate_desktop_file(applications_dir: Path, name: str, bin_content: str) -> None:
    dest = applications_dir / "{}.desktop".format(dash_case(name))
    entry = DesktopEntry(dest)
    entry.set("Name", name)
    entry.set("Exec", bin_content + " %u")
    # TODO customize icon?
    entry.set("Icon", "qutebrowser")
    # TODO allow additional categories
    entry.set("Categories", ["Network", "WebBrowser"])
    entry.set("Terminal", False)
    entry.set("StartupNotify", False)
    entry.set(
        "MimeType",
        [
            "text/html",
            "text/xml",
            "application/xhtml+xml",
            "application/xml",
            "application/rdf+xml",
            "image/gif",
            "image/jpeg",
            "image/png",
            "x-scheme-handler/http",
            "x-scheme-handler/https",
            "x-scheme-handler/qute",
        ],
    )
    entry.set("Keywords", ["Browser"])
    entry.write()


if __name__ == "__main__":
    main()
