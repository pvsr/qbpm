import platform
from collections.abc import Iterator
from pathlib import Path

from click import get_app_dir
from xdg_base_dirs import xdg_config_home, xdg_data_home


def qutebrowser_exe() -> str:
    macos_app = "/Applications/qutebrowser.app/Contents/MacOS/qutebrowser"
    if platform.system() == "Darwin" and Path(macos_app).exists():
        return macos_app
    else:
        return "qutebrowser"


def default_qbpm_config_dir() -> Path:
    return xdg_config_home() / "qbpm"


def default_qbpm_application_dir() -> Path:
    return xdg_data_home() / "applications" / "qbpm"


def default_profile_dir() -> Path:
    return xdg_data_home() / "qutebrowser-profiles"


def qutebrowser_data_dir() -> Path:
    if platform.system() == "Linux":
        return xdg_data_home() / "qutebrowser"
    # TODO confirm this works on windows
    return Path(get_app_dir("qutebrowser", roaming=True))


def qutebrowser_config_dirs() -> Iterator[Path]:
    app_dir = Path(get_app_dir("qutebrowser", roaming=True))
    yield app_dir
    xdg_dir = xdg_config_home() / "qutebrowser"
    if xdg_dir != app_dir:
        yield xdg_dir
    yield Path.home() / ".qutebrowser"
