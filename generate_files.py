from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Tuple, Optional

import toml
from jinja2 import Environment, FileSystemLoader
from xdg import BaseDirectory


ENV = Environment(loader=FileSystemLoader("templates"))


def main() -> None:
    # TODO argparse for:
    ## app name
    ## app url(s?)
    ## disable js by default (except in app url)?
    ## bin location (default to ~/bin)
    ## custom ssb.py
    ## Desktop info: generic name, types, keywords
    ## arbitrary qutebrowser options for ssb.py?
    ENV.filters["dashcase"] = dashcase
    ENV.globals = {
        "name": "test app",
        "url": "example.com",
        "basedir": "/tmp/qute-ssb-test/" + BaseDirectory.save_data_path("qute-ssb"),
        "bin": "/tmp/qute-ssb-test/" + str(Path.home()) + "/bin",
        "applications": "/tmp/qute-ssb-test/"
        + BaseDirectory.save_data_path("applications"),
    }

    tree = toml.loads(render("dir.toml"))
    for key, dirname in tree.items():
        generate_tree(key, dirname)


def render(name: str) -> str:
    # TODO check for TemplateNotFound
    return ENV.get_template(name).render()


def dashcase(string: str) -> str:
    return string.lower().replace(" ", "-")


# TODO xdg dirs
def generate_tree(key: str, tree: Mapping[str, Any]) -> None:
    # TODO allow relative paths in location?
    if not "location" in tree:
        print("warning: no location in", key)
        return
    location = Path(tree["location"])
    generate_dir(location, tree)


# TODO don't allow / in names
def generate_dir(dirname: Path, tree: Mapping[str, Any]) -> bool:
    overwrite = tree.get("overwrite", True)
    if not overwrite and dirname.exists():
        print("warning: " + str(dirname) + " already exists")
        return False
    print("mkdir file   ", dirname)
    # TODO don't commit until all paths are checked
    dirname.mkdir(parents=True, exist_ok=True)
    result = True
    for name, details in tree.get("files", {}).items():
        result &= generate_file(dirname / Path(name), details)
    for name, contents in tree.get("dirs", {}).items():
        result &= generate_dir(dirname / Path(name), contents)
    return result


class FileConstructorType(Enum):
    LINK = "link"
    TEMPLATE = "template"
    CONTENTS = "contents"


def generate_file(file: Path, details: Mapping[str, Any]) -> bool:
    overwrite = details.get("overwrite", True)
    if not overwrite and file.exists():
        print("warning: " + str(file) + " already exists")
        return False
    # TODO don't commit until all paths are checked
    print("generate file", file)
    constructor = get_constructor_type(details)
    if not constructor:
        return False
    c_type, value = constructor
    if c_type == FileConstructorType.LINK:
        print("linking:      " + value)
        file.symlink_to(resolve_xdg(value))
    elif c_type == FileConstructorType.TEMPLATE:
        print("template:     " + value)
        rendered = render(value)
        file.write_text(rendered)
    elif c_type == FileConstructorType.CONTENTS:
        print("contents:     " + value)
        file.write_text(value)
    else:
        print("unknown type")
        return False
    return True


def get_constructor_type(
    details: Mapping[str, Any]
) -> Optional[Tuple[FileConstructorType, str]]:
    present = [
        member
        for name, member in FileConstructorType.__members__.items()
        if member.value in details
    ]
    if len(present) != 1:
        print("error")
        return None
    return (present[0], details[present[0].value])


def resolve_xdg(path: str) -> Path:
    return Path(
        path.replace("$XDG_DATA_HOME", BaseDirectory.xdg_data_home)
        .replace("$XDG_CONFIG_HOME", BaseDirectory.xdg_config_home)
        .replace("$XDG_CACHE_HOME", BaseDirectory.xdg_cache_home)
    )


if __name__ == "__main__":
    main()
