from pathlib import Path

from qbpm.config import (
    DEFAULT_CONFIG_FILE,
    Config,
    find_config,
    find_qutebrowser_config_dir,
)

from . import no_homedir_fixture  # noqa: F401


def test_no_config():
    assert find_config(None) == Config.load(DEFAULT_CONFIG_FILE)


def test_empty_config(tmp_path: Path):
    file = tmp_path / "config.toml"
    file.touch()
    assert find_config(file) == Config()


def test_default_config_location(tmp_path: Path):
    (tmp_path / "qbpm").mkdir()
    (tmp_path / "qbpm" / "config.toml").touch()
    assert find_config(None) == Config()


def test_minimal_config(tmp_path: Path):
    file = tmp_path / "config.toml"
    file.write_text("""config_py_template = 'template'""")
    assert find_config(file) == Config(config_py_template="template")


def test_full_config(tmp_path: Path):
    file = tmp_path / "config.toml"
    file.write_text("""
config_py_template = \"""
config.load_autoconfig()
\"""
symlink_autoconfig = true
qutebrowser_config_directory = "~/.config/qutebrowser"
profile_directory = "profile"
generate_desktop_file = false
desktop_file_directory = "desktop"
menu = "~/bin/my-dmenu"
menu_prompt = "qbpm"
    """)
    assert find_config(file) == Config(
        config_py_template="config.load_autoconfig()\n",
        symlink_autoconfig=True,
        qutebrowser_config_directory=Path("~/.config/qutebrowser").expanduser(),
        profile_directory=Path("profile"),
        desktop_file_directory=Path("desktop"),
        generate_desktop_file=False,
        menu="~/bin/my-dmenu",
        menu_prompt="qbpm",
    )


def test_find_qb_config(tmp_path: Path):
    qb_dir = tmp_path / "qb"
    qb_conf_dir = qb_dir / "config"
    qb_conf_dir.mkdir(parents=True)
    (qb_conf_dir / "config.py").touch()
    assert find_qutebrowser_config_dir(qb_dir) == qb_conf_dir
    assert find_qutebrowser_config_dir(qb_dir / "config") == qb_conf_dir


def test_find_autoconfig(tmp_path: Path):
    qb_dir = tmp_path / "qb"
    qb_conf_dir = qb_dir / "config"
    qb_conf_dir.mkdir(parents=True)
    (qb_conf_dir / "autoconfig.yml").touch()
    assert find_qutebrowser_config_dir(qb_dir, autoconfig=True) == qb_conf_dir


def test_find_qb_config_default(tmp_path: Path):
    (tmp_path / "config.py").touch()
    assert find_qutebrowser_config_dir(None) == tmp_path


def test_find_qutebrowser_none(tmp_path: Path):
    assert find_qutebrowser_config_dir(None) is None
    assert find_qutebrowser_config_dir(tmp_path / "config") is None
