from os import chdir, environ
from pathlib import Path

from click.testing import CliRunner

from qbpm.main import main

from . import no_homedir_fixture  # noqa: F401


def run(*args: str):
    return CliRunner().invoke(main, args)


def test_profile_dir_option(tmp_path: Path):
    (tmp_path / "config.py").touch()
    result = run("-P", str(tmp_path), "new", "-C", str(tmp_path), "test")
    assert result.exit_code == 0
    assert result.output.strip() == str(tmp_path / "test")
    assert tmp_path / "test" in list(tmp_path.iterdir())


def test_profile_dir_env(tmp_path: Path):
    environ["QBPM_PROFILE_DIR"] = str(tmp_path)
    (tmp_path / "config.py").touch()
    result = run("new", "-C", str(tmp_path), "test")
    assert result.exit_code == 0
    assert result.output.strip() == str(tmp_path / "test")
    assert tmp_path / "test" in list(tmp_path.iterdir())


def test_config_dir_option(tmp_path: Path):
    environ["QBPM_PROFILE_DIR"] = str(tmp_path)
    config = tmp_path / "config.py"
    config.touch()
    result = run("new", "-C", str(tmp_path), "test")
    assert result.exit_code == 0
    assert str(config) in (tmp_path / "test/config/config.py").read_text()


def test_relative_config_dir(tmp_path: Path):
    environ["QBPM_PROFILE_DIR"] = str(tmp_path)
    config = tmp_path / "config.py"
    config.touch()
    chdir(tmp_path)
    result = run("new", "-C", ".", "test")
    assert result.exit_code == 0
    assert str(config) in (tmp_path / "test/config/config.py").read_text()


def test_from_session(tmp_path: Path):
    environ["QBPM_PROFILE_DIR"] = str(tmp_path)
    (tmp_path / "config.py").touch()
    session = tmp_path / "test.yml"
    session.write_text("windows:\n")
    result = run("from-session", "-C", str(tmp_path), str(session))
    assert result.exit_code == 0
    assert result.output.strip() == str(tmp_path / "test")
    assert (tmp_path / "test/data/sessions/_autosave.yml").read_text() == ("windows:\n")
