import textwrap
from pathlib import Path
from typing import Optional

from xdg_base_dirs import xdg_data_dirs, xdg_data_home

from . import Profile

MIME_TYPES = [
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
]


# TODO disable when not on linux?
# TODO expose application_dir through config
def create_desktop_file(
    profile: Profile, application_dir: Optional[Path] = None
) -> None:
    text = textwrap.dedent(f"""\
        [Desktop Entry]
        Name={profile.name} (qutebrowser profile)
        StartupWMClass=qutebrowser
        GenericName={profile.name}
        Icon=qutebrowser
        Type=Application
        Categories=Network;WebBrowser;
        Exec={" ".join([*profile.cmdline(), "--untrusted-args", "%u"])}
        Terminal=false
        StartupNotify=true
        MimeType={";".join(MIME_TYPES)};
        Keywords=Browser
        Actions=new-window;preferences;

        [Desktop Action new-window]
        Name=New Window
        Exec={" ".join(profile.cmdline())}

        [Desktop Action preferences]
        Name=Preferences
        Exec={" ".join([*profile.cmdline(), '"qute://settings"'])}
    """)
    application_dir = application_dir or default_qbpm_application_dir()
    (application_dir / f"{profile.name}.desktop").write_text(text)


def default_qbpm_application_dir() -> Path:
    path = xdg_data_home() / "applications" / "qbpm"
    path.mkdir(parents=True, exist_ok=True)
    return path
