import sys
import argparse
from pathlib import Path
from typing import Mapping, Optional, Callable, Dict

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


def main() -> None:
    # TODO argparse for:
    ## Desktop info: generic name, types, keywords
    ## arbitrary qutebrowser options for ssb.py?
    parser = argparse.ArgumentParser(description="program desc")
    parser.add_argument(
        "name",
        help='user-friendly name of your qutebrowser profile, e.g. "Python" or "My Cool Webapp"',
    )
    # TODO get default from config file?
    parser.add_argument(
        "-p",
        "--profile-location",
        metavar="DIR",
        type=Path,
        default=Path(BaseDirectory.save_data_path("qute-profiles")),
        help="location of qute-profile configurations, defaults to $XDG_DATA_HOME/qute-profiles",
    )

    parser.add_argument(
        "--prefix",
        metavar="DIR",
        nargs="?",
        default="qute-profiles",
        help="group qute-profile binaries and desktop files in a directory called DIR."
        + ' defaults to "qute-profiles", call without an argument to disable',
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
        "-B", "--no-bin", action="store_true", help="disable binary generation"
    )
    parser.add_argument(
        "-D",
        "--no-desktop",
        action="store_true",
        help="disable desktop file generation",
    )

    parser.add_argument(
        "-t",
        "--copy-type",
        choices=["symlink", "copy"],
        default="symlink",
        help="how to reference files from the source profile. defaults to symlink",
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
        help="custom qutebrowser configuration file",
    )
    parser.add_argument(
        "-C",
        "--custom-profile-location",
        type=Path,
        default=Path(),
        help="location of custom profile, relative to base config dir",
    )
    conf = parser.add_mutually_exclusive_group()
    conf.add_argument("--no-copy-config", action="store_true", help="bin")
    conf.add_argument(
        "--qb-config-dir",
        type=Path,
        default=Path(BaseDirectory.save_config_path("qutebrowser")),
        help="bin",
    )
    data = parser.add_mutually_exclusive_group()
    data.add_argument("--no-copy-data", action="store_true", help="bin")
    data.add_argument(
        "--qb-data-dir",
        type=Path,
        default=Path(BaseDirectory.save_data_path("qutebrowser")),
        help="bin",
    )

    parser.add_argument("-u", "--home-page", nargs="+", help="name")
    # TODO dry run
    parser.add_argument("-n", "--dry-run", action="store_true", help="dry-run")
    # TODO debug
    # TODO files to not copy/link. should probably be in a config too
    # by default should probably include data/{sessions, webengine} at least
    # maybe history should always be copied?
    # parser.add_argument("-i", "--ignore")
    args = parser.parse_args()

    if args.no_desktop:
        args.desktop = None
    else:
        args.desktop = Path(BaseDirectory.save_data_path("applications"))
        if args.prefix:
            args.desktop = args.desktop / args.prefix

    if args.no_bin:
        args.bin = None
    elif args.prefix:
        args.bin = args.bin / args.prefix

    ENV.globals = {"urls": args.home_page}

    dest = args.profile_location / args.name
    if dest.exists():
        print("Error: {} already exists".format(dest), file=sys.stderr)
        sys.exit(1)

    bin_content = "qutebrowser --basedir \"{basedir}/{name}\"".format(
        basedir=args.profile_location, name=dash_case(args.name)
    )

    src_roots: Dict[str, Path] = {}
    if not args.no_copy_config and args.qb_config_dir:
        src_roots["config"] = args.qb_config_dir
    if not args.no_copy_data and args.qb_data_dir:
        src_roots["data"] = args.qb_data_dir

    dest = args.profile_location / dash_case(args.name)
    if args.copy_type == "copy":
        clone(dest, src_roots, copy)
    elif args.copy_type == "symlink":
        clone(dest, src_roots, lambda src, dest: dest.symlink_to(src))

    if args.ssb:
        profile = dest / "config" / args.custom_profile_location / "profile.py"
        profile.parent.mkdir(parents=True, exist_ok=True)
        profile.write_text(render("profile.py"))
        with open(profile, "w") as f:
            f.write(render("profile.py"))
    elif args.custom_profile:
        profile = dest / "config" / args.custom_profile_location / "profile.py"
        profile.parent.mkdir(parents=True, exist_ok=True)
        # TODO treat custom prof as template?
        profile.write_text(args.custom_profile.read())

    if args.desktop:
        generate_desktop_file(args.desktop, args.name, bin_content)


def copy(src: Path, dest: Path) -> None:
    dest.write_bytes(src.read_bytes())


def clone(
    dest: Path, src_roots: Mapping[str, Path], file_op: Callable[[Path, Path], None]
) -> None:
    # TODO check src.is_dir()
    for dirname, src_root in src_roots.items():
        dest_root = dest / dirname
        if dest_root.exists():
            print("Error: {} already exists".format(dest_root), file=sys.stderr)
            sys.exit(1)
        else:
            dest_root.mkdir(parents=True)
            walk(src_root, dest_root, file_op)


def walk(
    src_root: Path, dest_root: Path, file_op: Callable[[Path, Path], None]
) -> None:
    # TODO subtract ignored
    for src in src_root.expanduser().resolve().glob("**/*"):
        dest = dest_root / src.relative_to(src_root)
        if src.is_dir():
            dest.mkdir()
        else:
            file_op(src, dest)


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
