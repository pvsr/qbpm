import shutil
import sys
from pathlib import Path

from . import Profile, profiles
from .config import Config
from .log import error, or_phrase
from .paths import qutebrowser_data_dir


def profile_from_session(
    session: str,
    profile_name: str | None,
    config: Config,
    overwrite: bool = False,
) -> Profile | None:
    profile, session_path = session_info(
        session, profile_name, config.profile_directory
    )
    if not profiles.new_profile(profile, config, None, overwrite):
        return None

    session_dir = profile.root / "data" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=overwrite)
    shutil.copy(session_path, session_dir / "_autosave.yml")

    return profile


def session_info(
    session: str, profile_name: str | None, profile_dir: Path
) -> tuple[Profile, Path]:
    user_session_dir = qutebrowser_data_dir() / "sessions"
    session_paths = []
    if "/" not in session:
        session_paths.append(user_session_dir / (session + ".yml"))
    session_paths.append(Path(session))
    session_path = next(filter(lambda path: path.is_file(), session_paths), None)

    if session_path:
        return (
            Profile(
                profile_name or session_path.stem,
                profile_dir,
            ),
            session_path,
        )
    tried = or_phrase([str(p.resolve()) for p in session_paths])
    error(f"could not find session file at {tried}")
    sys.exit(1)
