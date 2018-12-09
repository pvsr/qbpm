from pathlib import Path
from typing import Any, Mapping

import toml
from jinja2 import Environment, FileSystemLoader


def main() -> None:
    # TODO argparse for:
    ## app name
    ## app url(s?)
    ## disable js by default (except in app url)?
    ## bin location (default to ~/bin)
    ## custom ssb.py
    ## Desktop info: generic name, types, keywords
    ## arbitrary qutebrowser options for ssb.py?
    env = Environment(loader=FileSystemLoader("templates"))
    env.filters["dashcase"] = dashcase
    dir_template = env.get_template("dir.toml")
    rendered = dir_template.render(
        name="test app", url="example.com", bin="/tmp/qute-ssb-test/bin"
    )
    tree = toml.loads(rendered)
    for key, dirname in tree.items():
        generate_tree(key, dirname)


def dashcase(string: str) -> str:
    return string.lower().replace(" ", "-")


# TODO xdg dirs
def generate_tree(key: str, tree: Mapping[str, Any]) -> None:
    if not "location" in tree:
        print("warning: no location in", key)
        return
    location = Path(tree["location"])
    generate_dir(location, tree)


# TODO don't allow / in names
def generate_dir(dirname: Path, tree: Mapping[str, Any]) -> None:
    print("mkdir file   ", dirname)
    for name, details in tree.get("files", {}).items():
        generate_file(dirname / Path(name), details)
    for name, contents in tree.get("dirs", {}).items():
        generate_dir(dirname / Path(name), contents)


def generate_file(file: Path, details: Mapping[str, Any]) -> None:
    print("generate file", file)


if __name__ == "__main__":
    main()
