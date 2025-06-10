from os import environ
from pathlib import Path

from qbpm.choose import choose_profile, find_menu


def write_script(parent_dir: Path, name: str = "menu", contents: str = "") -> Path:
    parent_dir.mkdir(exist_ok=True)
    menu = parent_dir / name
    menu.write_text(f"#!/bin/sh\n{contents}")
    menu.chmod(0o700)
    return menu


def test_choose(tmp_path: Path):
    log = tmp_path / "log"
    log.touch()
    menu = write_script(tmp_path / "bin", contents=f"cat > {log}\necho p1")
    write_script(
        tmp_path / "bin",
        name="qutebrowser",
        contents=f'echo qutebrowser "$@" >> {log}',
    )
    environ["PATH"] = str(tmp_path / "bin") + ":" + environ["PATH"]

    profile_dir = tmp_path / "profiles"
    profile_dir.mkdir()
    (profile_dir / "p1").mkdir()
    (profile_dir / "p2").mkdir()
    assert choose_profile(profile_dir, str(menu), False, ())
    assert log.read_text().startswith(
        f"""p1
p2
qutebrowser
qutebrowser -B {profile_dir / "p1"}"""
    )


def test_find_installed_menu(tmp_path: Path):
    write_script(tmp_path / "bin", name="dmenu")
    environ["PATH"] = str(tmp_path / "bin")
    environ["DISPLAY"] = ":1"
    assert getattr(find_menu(None), "name", None) == "dmenu"


def test_override_menu_priority(tmp_path: Path):
    write_script(tmp_path / "bin", name="fuzzel")
    write_script(tmp_path / "bin", name="dmenu-wl")
    environ["PATH"] = str(tmp_path / "bin")
    environ["WAYLAND_DISPLAY"] = "wayland-2"
    assert getattr(find_menu(None), "name", None) == "fuzzel"
    assert getattr(find_menu("dmenu-wl"), "name", None) == "dmenu-wl"


def test_custom_menu():
    dmenu = find_menu("/bin/sh -c")
    assert dmenu is not None
    assert (
        dmenu.commandline(["p1", "p2"], "", "").strip() == 'echo "p1\np2" | /bin/sh -c'
    )


def test_invalid_custom_menu():
    assert find_menu("fake_command") is None


def test_custom_menu_space_in_name(tmp_path: Path):
    write_script(tmp_path / "bin", name="my menu")
    environ["PATH"] = str(tmp_path / "bin")
    environ["DISPLAY"] = ":1"
    dmenu = find_menu("my\\ menu")
    assert dmenu is not None
    assert dmenu.installed()


def test_custom_menu_default_args(tmp_path: Path):
    menu = write_script(tmp_path / "bin", name="rofi")
    environ["PATH"] = str(tmp_path / "bin")
    environ["DISPLAY"] = ":1"
    dmenu = find_menu(str(menu))
    assert dmenu is not None
    assert f"{menu} -dmenu -no-custom -p ''" in dmenu.commandline(["p1", "p2"], "", "")


def test_custom_menu_custom_args(tmp_path: Path):
    menu = write_script(tmp_path / "bin", name="rofi")
    command = f"{menu} -custom -dmenu"
    environ["PATH"] = str(tmp_path / "bin")
    environ["DISPLAY"] = ":1"
    dmenu = find_menu(command)
    assert dmenu is not None
    assert dmenu.commandline(["p1", "p2"], "", "").endswith(command)
