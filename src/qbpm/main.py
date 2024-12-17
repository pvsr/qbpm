import logging
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NoReturn

import click

from . import Profile, operations, profiles
from .choose import choose_profile
from .launch import launch_qutebrowser
from .menus import supported_menus
from .paths import default_profile_dir, qutebrowser_data_dir
from .utils import error, or_phrase

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@dataclass
class Context:
    profile_dir: Path


def creator_options(f: Callable[..., Any]) -> Callable[..., Any]:
    for opt in reversed(
        [
            click.option(
                "-C",
                "--qutebrowser-config-dir",
                "qb_config_dir",
                type=click.Path(file_okay=False, readable=True, path_type=Path),
                help="Location of the qutebrowser config to inherit from.",
            ),
            click.option("-l", "--launch", is_flag=True, help="Launch the profile."),
            click.option(
                "-f",
                "--foreground",
                is_flag=True,
                help="If --launch is set, run qutebrowser in the foreground.",
            ),
            click.option(
                "--no-desktop-file",
                "desktop_file",
                default=True,
                is_flag=True,
                flag_value=False,
                help="Do not generate an XDG desktop entry for the profile.",
            ),
            click.option(
                "--overwrite",
                is_flag=True,
                help="Replace the current profile configuration if it exists.",
            ),
        ]
    ):
        f = opt(f)
    return f


class LowerCaseFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.levelname = record.levelname.lower()
        return super().format(record)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
@click.option(
    "-P",
    "--profile-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    envvar="QBPM_PROFILE_DIR",
    show_envvar=True,
    default=None,
    help="Location to store qutebrowser profiles.",
)
@click.option(
    "-l",
    "--log-level",
    default="error",
    type=click.Choice(["debug", "info", "error"], case_sensitive=False),
)
@click.pass_context
def main(ctx: click.Context, profile_dir: Path | None, log_level: str) -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())
    handler = logging.StreamHandler()
    handler.setFormatter(LowerCaseFormatter("{levelname}: {message}", style="{"))
    root_logger.addHandler(handler)
    ctx.obj = Context(profile_dir or default_profile_dir())


@main.command()
@click.argument("profile_name")
@click.argument("home_page", required=False)
@creator_options
@click.pass_obj
def new(context: Context, profile_name: str, **kwargs: Any) -> None:
    """Create a new profile."""
    profile = Profile(profile_name, **vars(context))
    then_launch(profiles.new_profile, profile, **kwargs)


@main.command()
@click.argument("session")
@click.argument("profile_name", required=False)
@creator_options
@click.pass_obj
def from_session(
    context: Context,
    session: str,
    profile_name: str | None,
    **kwargs: Any,
) -> None:
    """Create a new profile from a saved qutebrowser session.
    SESSION may be the name of a session in the global qutebrowser profile
    or a path to a session yaml file.
    """
    profile, session_path = session_info(session, profile_name, context)
    then_launch(operations.from_session, profile, session_path=session_path, **kwargs)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("profile_name")
@click.argument("qb_args", nargs=-1, type=click.UNPROCESSED)
@click.option(
    "-f", "--foreground", is_flag=True, help="Run qutebrowser in the foreground."
)
@click.pass_obj
def launch(context: Context, profile_name: str, **kwargs: Any) -> None:
    """Launch qutebrowser with a specific profile. All QB_ARGS are passed on to qutebrowser."""
    profile = Profile(profile_name, **vars(context))
    exit_with(launch_qutebrowser(profile, **kwargs))


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("qb_args", nargs=-1, type=click.UNPROCESSED)
@click.option(
    "-m",
    "--menu",
    metavar="COMMAND",
    help="A dmenu-compatible command or one of the following supported menus: "
    + ", ".join(sorted([getattr(m, "name", "applescript") for m in supported_menus()])),
)
@click.option(
    "-f", "--foreground", is_flag=True, help="Run qutebrowser in the foreground."
)
@click.pass_obj
def choose(context: Context, **kwargs: Any) -> None:
    """Choose a profile to launch.
    Support is built in for many X and Wayland launchers, as well as applescript dialogs.
    All QB_ARGS are passed on to qutebrowser.
    """
    exit_with(choose_profile(profile_dir=context.profile_dir, **kwargs))


@main.command()
@click.argument("profile_name")
@click.pass_obj
def edit(context: Context, profile_name: str) -> None:
    """Edit a profile's config.py."""
    profile = Profile(profile_name, **vars(context))
    if not profile.exists():
        error(f"profile {profile.name} not found at {profile.root}")
        sys.exit(1)
    click.edit(filename=str(profile.root / "config" / "config.py"))


@main.command(name="list")
@click.pass_obj
def list_(context: Context) -> None:
    """List existing profiles."""
    for profile in sorted(context.profile_dir.iterdir()):
        print(profile.name)


@main.command()
@click.argument("profile_name")
@click.pass_obj
def desktop(
    context: Context,
    profile_name: str,
) -> None:
    """Create an XDG desktop entry for an existing profile."""
    profile = Profile(profile_name, **vars(context))
    exit_with(operations.desktop(profile))


def then_launch(
    operation: Callable[..., bool],
    profile: Profile,
    launch: bool,
    foreground: bool,
    qb_args: tuple[str, ...] = (),
    **kwargs: Any,
) -> None:
    exit_with(
        operation(profile, **kwargs)
        and ((not launch) or launch_qutebrowser(profile, foreground, qb_args))
    )


def session_info(
    session: str, profile_name: str | None, context: Context
) -> tuple[Profile, Path]:
    user_session_dir = qutebrowser_data_dir() / "sessions"
    session_paths = []
    if "/" not in session:
        session_paths.append(user_session_dir / (session + ".yml"))
    session_paths.append(Path(session))
    session_path = next(filter(lambda path: path.is_file(), session_paths), None)

    if not session_path:
        tried = or_phrase([str(p.resolve()) for p in session_paths])
        error(f"could not find session file at {tried}")
        sys.exit(1)

    return (Profile(profile_name or session_path.stem, **vars(context)), session_path)


def exit_with(result: bool) -> NoReturn:
    sys.exit(0 if result else 1)
