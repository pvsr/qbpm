import inspect
from os import environ
from pathlib import Path
from typing import Any, Callable, Optional

import click
from xdg import BaseDirectory

from . import __version__, operations, profiles
from .profiles import Profile
from .utils import SUPPORTED_MENUS, default_profile_dir, error

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-P",
    "--profile-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    envvar="QBPM_PROFILE_DIR",
    default=default_profile_dir,
)
@click.pass_context
def main(ctx, profile_dir: Path) -> None:
    # TODO version, documentation
    # TODO -h as --help
    ctx.ensure_object(dict)
    ctx.obj["PROFILE_DIR"] = profile_dir


@main.command()
@click.argument("profile_name")
@click.argument("home_page", required=False)
@click.option("--desktop-file/--no-desktop-file", default=True, is_flag=True)
@click.option("--overwrite", is_flag=True)
@click.option("-l", "--launch", is_flag=True)
@click.option("-f", "--foreground", is_flag=True)
@click.pass_context
def new(ctx, profile_name: str, launch: bool, foreground: bool, **kwargs):
    profile = Profile(profile_name, ctx.obj["PROFILE_DIR"])
    result = profiles.new_profile(profile, **kwargs)
    if result and launch:
        # TODO args?
        exit_with(then_launch(profile, foreground, []))
    exit_with(result)


@main.command()
@click.argument("session")
@click.argument("profile_name", required=False)
@click.option("--desktop-file/--no-desktop-file", default=True, is_flag=True)
@click.option("--overwrite", is_flag=True)
@click.option("-l", "--launch", is_flag=True)
@click.option("-f", "--foreground", is_flag=True)
@click.pass_context
def from_session(
    ctx,
    launch: bool,
    foreground: bool,
    **kwargs,
):
    profile = operations.from_session(profile_dir=ctx.obj["PROFILE_DIR"], **kwargs)
    if profile and launch:
        # TODO args?
        exit_with(then_launch(profile, foreground, []))
    exit_with(bool(profile))


@main.command()
@click.argument("profile_name")
@click.pass_context
def desktop(
    ctx,
    profile_name: str,
):
    profile = Profile(profile_name, ctx.obj["PROFILE_DIR"])
    exit_with(operations.desktop(profile))


@main.command()
@click.argument("profile_name")
@click.option("-c", "--create", is_flag=True)
@click.option("-f", "--foreground", is_flag=True)
@click.pass_context
def launch(ctx, profile_name: str, **kwargs):
    profile = Profile(profile_name, ctx.obj["PROFILE_DIR"])
    # TODO qb args
    exit_with(operations.launch(profile, **kwargs))


@main.command()
@click.option("-m", "--menu")
@click.option("-f", "--foreground", is_flag=True)
@click.pass_context
def choose(ctx, **kwargs):
    # TODO qb args
    exit_with(
        operations.choose(profile_dir=ctx.obj["PROFILE_DIR"], qb_args=[], **kwargs)
    )


@main.command()
@click.argument("profile_name")
@click.pass_context
def edit(ctx, profile_name):
    breakpoint()
    profile = Profile(profile_name, ctx.obj["PROFILE_DIR"])
    if not profile.exists():
        error(f"profile {profile.name} not found at {profile.root}")
        exit(1)
    click.edit(filename=profile.root / "config" / "config.py")


@main.command(name="list")
@click.pass_context
def list_(ctx):
    for profile in sorted(ctx.obj["PROFILE_DIR"].iterdir()):
        print(profile.name)


def then_launch(profile: Profile, foreground: bool, qb_args: list[str]) -> bool:
    result = False
    if profile:
        result = operations.launch(profile, False, foreground, qb_args)
    return result


def exit_with(result: bool):
    exit(0 if result else 1)


if __name__ == "__main__":
    main(obj={})
