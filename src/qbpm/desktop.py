import textwrap
from pathlib import Path

from . import Profile
from .paths import default_qbpm_application_dir

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


# TODO expose application_dir through config
def create_desktop_file(profile: Profile, application_dir: Path | None = None) -> None:
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
