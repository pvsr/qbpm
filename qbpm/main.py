import inspect
from os import environ
from pathlib import Path
from typing import Any, Callable, Optional

import click
from xdg import BaseDirectory

from . import __version__, operations, profiles
from .profiles import Profile
from .utils import SUPPORTED_MENUS, default_profile_dir, error, user_data_dir

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-P",
    "--profile-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    envvar="QBPM_PROFILE_DIR",
    default=default_profile_dir,
    help="directory in which profiles are stored",
)
@click.pass_context
def main(ctx, profile_dir: Path) -> None:
    # TODO version
    ctx.obj = profile_dir


@main.command()
@click.argument("profile_name")
@click.argument("home_page", required=False)
@click.option("--desktop-file/--no-desktop-file", default=True, is_flag=True)
@click.option("--overwrite", is_flag=True)
@click.option("-l", "--launch", is_flag=True)
@click.option("-f", "--foreground", is_flag=True)
@click.pass_obj
def new(profile_dir: Path, profile_name: str, **kwargs):
    """Create a new profile."""
    profile = Profile(profile_name, profile_dir)
    then_launch(profiles.new_profile, profile, **kwargs)


@main.command()
@click.argument("session")
@click.argument("profile_name", required=False)
@click.option("--desktop-file/--no-desktop-file", default=True, is_flag=True)
@click.option("--overwrite", is_flag=True)
@click.option("-l", "--launch", is_flag=True)
@click.option("-f", "--foreground", is_flag=True)
@click.pass_obj
def from_session(
    profile_dir: Path,
    session: str,
    profile_name: Optional[str],
    **kwargs,
):
    """Create a new profile from a saved qutebrowser session.
    SESSION may be the name of a session in the global qutebrowser profile
    or a path to a session yaml file.
    """
    profile, session_path = session_info(session, profile_name, profile_dir)
    then_launch(operations.from_session, profile, session_path=session_path, **kwargs)


@main.command()
@click.argument("profile_name")
@click.pass_obj
def desktop(
    profile_dir: Path,
    profile_name: str,
):
    """Create a desktop file for an existing profile."""
    profile = Profile(profile_name, profile_dir)
    exit_with(operations.desktop(profile))


@main.command()
@click.argument("profile_name")
@click.option("-c", "--create", is_flag=True)
@click.option("-f", "--foreground", is_flag=True)
@click.pass_obj
def launch(profile_dir: Path, profile_name: str, **kwargs):
    """Launch qutebrowser with a specific profile."""
    profile = Profile(profile_name, profile_dir)
    # TODO qb args
    exit_with(operations.launch(profile, qb_args=[], **kwargs))


@main.command()
@click.option(
    "-m",
    "--menu",
    metavar="COMMAND",
    help=f"A dmenu-compatible command or one of the following supported menus: {', '.join(sorted(SUPPORTED_MENUS))}",
)
@click.option("-f", "--foreground", is_flag=True)
@click.pass_obj
def choose(profile_dir: Path, **kwargs):
    """Choose a profile to launch.
    Support is built in for many X and Wayland launchers, as well as applescript dialogs.
    """
    # TODO qb args
    exit_with(operations.choose(profile_dir=profile_dir, qb_args=[], **kwargs))


@main.command()
@click.argument("profile_name")
@click.pass_obj
def edit(profile_dir: Path, profile_name):
    """Edit a profile's config.py."""
    profile = Profile(profile_name, profile_dir)
    if not profile.exists():
        error(f"profile {profile.name} not found at {profile.root}")
        exit(1)
    click.edit(filename=profile.root / "config" / "config.py")


@main.command(name="list")
@click.pass_obj
def list_(profile_dir: Path):
    """List existing profiles."""
    for profile in sorted(profile_dir.iterdir()):
        print(profile.name)


def then_launch(
    operation: Callable[..., bool],
    profile: Profile,
    launch: bool,
    foreground: bool,
    qb_args: list[str] = [],
    **kwargs,
) -> None:
    exit_with(
        operation(profile, **kwargs)
        and ((not launch) or operations.launch(profile, False, foreground, qb_args))
    )


def session_info(
    session: str, profile_name: Optional[str], profile_dir: Path
) -> tuple[Profile, Path]:
    user_session_dir = user_data_dir() / "sessions"
    session_paths = []
    if not "/" in session:
        session_paths.append(user_session_dir / (session + ".yml"))
    session_paths.append(Path(session))
    session_path = next(filter(lambda path: path.is_file(), session_paths), None)

    if not session_path:
        tried = ", ".join([str(p.resolve()) for p in session_paths])
        error(f"could not find session at the following paths: {tried}")
        exit(1)

    return (Profile(profile_name or session_path.stem, profile_dir), session_path)


def exit_with(result: bool):
    exit(0 if result else 1)
