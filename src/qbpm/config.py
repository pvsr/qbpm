import os
import platform
import sys
import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path

import dacite

from . import paths
from .log import error, or_phrase

DEFAULT_CONFIG_FILE = Path(__file__).parent / "config.toml"


@dataclass(kw_only=True)
class Config:
    config_py_template: str | None = None
    symlink_autoconfig: bool = False
    qutebrowser_config_directory: Path | None = None
    profile_directory: Path = field(default_factory=paths.default_profile_dir)
    generate_desktop_file: bool = platform.system() == "Linux"
    desktop_file_directory: Path = field(
        default_factory=paths.default_qbpm_application_dir
    )
    menu: str | list[str] = field(default_factory=list)
    menu_prompt: str = "qutebrowser"

    @classmethod
    def load(cls, config_file: Path | None) -> "Config":
        config_file = config_file or DEFAULT_CONFIG_FILE
        try:
            data = tomllib.loads(config_file.read_text(encoding="utf-8"))
            if extra := data.keys() - {field.name for field in fields(Config)}:
                raise RuntimeError(f'unknown config value: "{next(iter(extra))}"')
            return dacite.from_dict(
                data_class=Config,
                data=data,
                config=dacite.Config(
                    type_hooks={Path: lambda val: Path(val).expanduser()}
                ),
            )
        except Exception as e:
            error(f"loading {config_file} failed with error '{e}'")
            sys.exit(1)


def find_config(config_path: Path | None) -> Config:
    if not config_path:
        default = paths.default_qbpm_config_dir() / "config.toml"
        if default.is_file():
            config_path = default
    elif config_path == Path(os.devnull):
        config_path = None
    elif not config_path.is_file():
        error(f"{config_path} is not a file")
        sys.exit(1)
    return Config.load(config_path)


def find_qutebrowser_config_dir(
    qb_config_dir: Path | None, autoconfig: bool = False
) -> Path | None:
    dirs = (
        [qb_config_dir, qb_config_dir / "config"]
        if qb_config_dir
        else list(paths.qutebrowser_config_dirs())
    )
    for config_dir in dirs:
        if (config_dir / "config.py").exists() or (
            autoconfig and (config_dir / "autoconfig.yml").exists()
        ):
            return config_dir.absolute()
    if autoconfig:
        error(f"couldn't find config.py or autoconfig.yml in {or_phrase(dirs)}")
    else:
        error(f"couldn't find config.py in {or_phrase(dirs)}")
    return None
