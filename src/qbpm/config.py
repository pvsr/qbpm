import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from dacite import from_dict

from . import paths
from .log import error, or_phrase
from .paths import default_qbpm_config_dir, qutebrowser_config_dirs

DEFAULT_CONFIG_FILE = Path(__file__).parent / "config.toml"


@dataclass(kw_only=True)
class Config:
    profile_directory: Path = field(default_factory=paths.default_profile_dir)
    config_py_template: str
    qutebrowser_config_directory: Path = field(
        default_factory=lambda: find_qutebrowser_config_dir(None)
    )
    desktop_file_directory: Path = field(
        default_factory=paths.default_qbpm_application_dir
    )
    generate_desktop_file: bool = True
    menu: list[str] = field(default_factory=list)
    prompt: str = "qbpm"

    @classmethod
    def load(cls, config_file: Path) -> "Config":
        return from_dict(
            Config, data=tomllib.loads(config_file.read_text(encoding="utf-8"))
        )

    @classmethod
    def default(cls) -> "Config":
        return cls.load(DEFAULT_CONFIG_FILE)


def load_config(config_path: Path | None) -> Config | None:
    if not config_path:
        default = default_qbpm_config_dir() / "config.toml"
        if default.is_file():
            config_path = default
    elif not config_path.is_file():
        print("error")
        return None
        # sys.exit(1)

    if config_path:
        return Config.load(config_path)
    return None


def find_qutebrowser_config_dir(qb_config_dir: Path | None) -> Path:
    config_file = "config.py"
    dirs = (
        [qb_config_dir, qb_config_dir / "config"]
        if qb_config_dir
        else qutebrowser_config_dirs()
    )
    for config_dir in dirs:
        if (config_dir / config_file).exists():
            return config_dir.absolute()
    error(f"could not find {config_file} in {or_phrase(dirs)}")
    sys.exit(1)
