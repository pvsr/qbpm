import platform
from pathlib import Path

from click import get_app_dir
from xdg_base_dirs import xdg_config_home, xdg_data_home


def qutebrowser_exe() -> str:
    macos_app = "/Applications/qutebrowser.app/Contents/MacOS/qutebrowser"
    if platform == "darwin" and Path(macos_app).exists():
        return macos_app
    else:
        return "qutebrowser"


def default_qbpm_application_dir() -> Path:
    path = xdg_data_home() / "applications" / "qbpm"
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_profile_dir() -> Path:
    path = xdg_data_home() / "qutebrowser-profiles"
    path.mkdir(parents=True, exist_ok=True)
    return path


def qutebrowser_data_dir() -> Path:
    if platform.system() == "Linux":
        return xdg_data_home() / "qutebrowser"
    # TODO confirm this works on windows
    return Path(get_app_dir("qutebrowser", roaming=True))


def qutebrowser_config_dirs() -> list[Path]:
    # deduplicate while maintaining order
    return list(
        dict.fromkeys(
            [
                Path(get_app_dir("qutebrowser", roaming=True)),
                xdg_config_home() / "qutebrowser",
                Path.home() / ".qutebrowser",
            ]
        )
    )
