import logging
import sys
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, NoReturn, TypeVar

import click

from . import Profile, profiles
from .choose import choose_profile
from .config import DEFAULT_CONFIG_FILE, Config, find_config
from .desktop import create_desktop_file
from .launch import launch_qutebrowser
from .menus import supported_menus
from .paths import default_qbpm_config_dir
from .session import profile_from_session

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"], "max_content_width": 91}


@dataclass
class Context:
    cli_profile_dir: Path | None
    cli_config_file: Path | None

    def load_config(self) -> Config:
        config = find_config(self.cli_config_file)
        if self.cli_profile_dir:
            config.profile_directory = self.cli_profile_dir
        return config


@dataclass
class CreatorOptions:
    qb_config_dir: Path | None
    launch: bool
    foreground: bool
    desktop_file: bool | None
    overwrite: bool


T = TypeVar("T")


def creator_options(orig: Callable[..., T]) -> Callable[..., T]:
    @wraps(orig)
    def command(
        qb_config_dir: Path | None,
        launch: bool,
        foreground: bool,
        desktop_file: bool | None,
        overwrite: bool,
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> T:
        return orig(
            *args,
            c_opts=CreatorOptions(
                qb_config_dir, launch, foreground, desktop_file, overwrite
            ),
            **kwargs,
        )

    for opt in reversed(
        [
            click.option(
                "-C",
                "--qutebrowser-config-dir",
                "qb_config_dir",
                type=click.Path(file_okay=False, readable=True, path_type=Path),
                help="Location of the qutebrowser config to source.",
            ),
            click.option("-l", "--launch", is_flag=True, help="Launch the profile."),
            click.option(
                "-f",
                "--foreground",
                is_flag=True,
                help="If --launch is set, run qutebrowser in the foreground.",
            ),
            click.option(
                "--desktop-file/--no-desktop-file",
                default=None,
                help="Generate an XDG desktop entry for the profile.",
            ),
            click.option(
                "--overwrite",
                is_flag=True,
                help="Replace the current profile configuration if it exists.",
            ),
        ]
    ):
        command = opt(command)
    return command


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
    show_envvar=False,
    default=None,
    help="Location to store qutebrowser profiles.",
)
@click.option(
    "-c",
    "--config-file",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    help="Location of qbpm config file.",
)
@click.option(
    "-l",
    "--log-level",
    default="error",
    type=click.Choice(["debug", "info", "error"], case_sensitive=False),
)
@click.pass_context
def main(
    ctx: click.Context,
    profile_dir: Path | None,
    config_file: Path | None,
    log_level: str,
) -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())
    handler = logging.StreamHandler()
    handler.setFormatter(LowerCaseFormatter("{levelname}: {message}", style="{"))
    root_logger.addHandler(handler)
    ctx.obj = Context(profile_dir, config_file)


@main.command()
@click.argument("profile_name")
@click.argument("home_page", required=False)
@creator_options
@click.pass_obj
def new(
    context: Context,
    profile_name: str,
    home_page: str | None,
    c_opts: CreatorOptions,
) -> None:
    """Create a new profile."""
    config = context.load_config()
    profile = Profile(profile_name, config.profile_directory)
    if c_opts.qb_config_dir:
        config.qutebrowser_config_directory = c_opts.qb_config_dir.absolute()
    if c_opts.desktop_file is not None:
        config.generate_desktop_file = c_opts.desktop_file
    exit_with(
        profiles.new_profile(
            profile,
            config,
            home_page,
            c_opts.overwrite,
        )
        and ((not c_opts.launch) or launch_qutebrowser(profile, c_opts.foreground))
    )


@main.command()
@click.argument("session")
@click.argument("profile_name", required=False)
@creator_options
@click.pass_obj
def from_session(
    context: Context,
    session: str,
    profile_name: str | None,
    c_opts: CreatorOptions,
) -> None:
    """Create a new profile from a saved qutebrowser session.

    SESSION may be the name of a session in the global qutebrowser profile
    or a path to a session yaml file.
    """
    config = context.load_config()
    if c_opts.qb_config_dir:
        config.qutebrowser_config_directory = c_opts.qb_config_dir.absolute()
    if c_opts.desktop_file is not None:
        config.generate_desktop_file = c_opts.desktop_file
    profile = profile_from_session(
        session,
        profile_name,
        config,
        c_opts.overwrite,
    )
    exit_with(
        profile is not None
        and ((not c_opts.launch) or launch_qutebrowser(profile, c_opts.foreground))
    )


@main.command("launch", context_settings={"ignore_unknown_options": True})
@click.argument("profile_name")
@click.argument("qb_args", nargs=-1, type=click.UNPROCESSED)
@click.option(
    "-f", "--foreground", is_flag=True, help="Run qutebrowser in the foreground."
)
@click.pass_obj
def launch_profile(
    context: Context, profile_name: str, foreground: bool, qb_args: tuple[str, ...]
) -> None:
    """Launch qutebrowser with a specific profile.

    All QB_ARGS are passed on to qutebrowser."""
    profile = Profile(profile_name, context.load_config().profile_directory)
    if not profiles.check(profile):
        sys.exit(1)
    exit_with(launch_qutebrowser(profile, foreground, qb_args))


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("qb_args", nargs=-1, type=click.UNPROCESSED)
@click.option(
    "-m",
    "--menu",
    metavar="COMMAND",
    help="A dmenu-compatible command or one of the following supported menus: "
    + ", ".join([menu.name() for menu in supported_menus()]),
)
@click.option(
    "-f", "--foreground", is_flag=True, help="Run qutebrowser in the foreground."
)
@click.pass_obj
def choose(
    context: Context, menu: str | None, foreground: bool, qb_args: tuple[str, ...]
) -> None:
    """Choose a profile to launch.

    Support is built in for many X and Wayland launchers, as well as applescript dialogs.
    All QB_ARGS are passed on to qutebrowser.
    """
    config = context.load_config()
    exit_with(
        choose_profile(
            config.profile_directory,
            menu or config.menu,
            config.menu_prompt,
            foreground,
            qb_args,
        )
    )


@main.command()
@click.argument("profile_name")
@click.pass_obj
def edit(context: Context, profile_name: str) -> None:
    """Edit a profile's config.py."""
    profile = Profile(profile_name, context.load_config().profile_directory)
    if not profiles.check(profile):
        sys.exit(1)
    click.edit(filename=str(profile.root / "config" / "config.py"))


@main.command(name="list")
@click.pass_obj
def list_(context: Context) -> None:
    """List existing profiles."""
    for profile in sorted(context.load_config().profile_directory.iterdir()):
        print(profile.name)


@main.command()
@click.argument("profile_name")
@click.pass_obj
def desktop(
    context: Context,
    profile_name: str,
) -> None:
    """Create an XDG desktop entry for an existing profile."""
    config = context.load_config()
    profile = Profile(profile_name, config.profile_directory)
    exists = profiles.check(profile)
    if exists:
        create_desktop_file(profile, config.desktop_file_directory)
    exit_with(exists)


@main.group(context_settings={"help_option_names": []})
def config() -> None:
    """Commands to create a qbpm config file.

    qbpm config default > "$(qbpm config path)"
    """
    pass


@config.command()
@click.pass_obj
def path(context: Context) -> None:
    """Print the location where qbpm will look for a config file."""
    if context.cli_config_file:
        print(context.cli_config_file.absolute())
    else:
        config_dir = default_qbpm_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        print(config_dir / "config.toml")


@config.command
def default() -> None:
    """Print the default qbpm config file."""
    print(DEFAULT_CONFIG_FILE.read_text(), end="")


def exit_with(result: bool) -> NoReturn:
    sys.exit(0 if result else 1)
