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
    assert (tmp_path / "applications" / "qbpm" / "test.desktop").exists()


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


def test_from_session_path(tmp_path: Path):
    environ["QBPM_PROFILE_DIR"] = str(tmp_path)
    (tmp_path / "config.py").touch()
    session = tmp_path / "test.yml"
    session.write_text("windows:\n")
    result = run("from-session", "-C", str(tmp_path), str(session))
    assert result.exit_code == 0
    assert result.output.strip() == str(tmp_path / "test")
    assert (tmp_path / "test/data/sessions/_autosave.yml").read_text() == ("windows:\n")


def test_from_session_name(tmp_path: Path):
    environ["QBPM_PROFILE_DIR"] = str(tmp_path)
    (tmp_path / "config.py").touch()
    environ["XDG_DATA_HOME"] = str(tmp_path)
    (tmp_path / "qutebrowser" / "sessions").mkdir(parents=True)
    (tmp_path / "qutebrowser" / "sessions" / "test.yml").write_text("windows:\n")
    result = run("from-session", "-C", str(tmp_path), "test")
    assert result.exit_code == 0
    assert result.output.strip() == str(tmp_path / "test")
    assert (tmp_path / "test/data/sessions/_autosave.yml").read_text() == ("windows:\n")


def test_config_file(tmp_path: Path):
    environ["QBPM_PROFILE_DIR"] = str(tmp_path)
    (tmp_path / "config.py").touch()
    config_file = tmp_path / "config.toml"
    config_file.write_text("config_py_template = '# Custom template {profile_name}'")
    result = run("-c", str(config_file), "new", "test")
    assert result.exit_code == 0
    profile_config = tmp_path / "test" / "config" / "config.py"
    assert "# Custom template test" in profile_config.read_text()


def test_bad_config_file():
    result = run("-c", "/nonexistent/config.toml", "list")
    assert result.exit_code == 1
    assert "not a file" in result.output


def test_no_desktop_file(tmp_path: Path):
    environ["QBPM_PROFILE_DIR"] = str(tmp_path)
    (tmp_path / "config.py").touch()
    run("-P", str(tmp_path), "new", "--no-desktop-file", "-C", str(tmp_path), "test")
    assert not (tmp_path / "applications" / "qbpm" / "test.desktop").exists()


def test_desktop_file_directory(tmp_path: Path):
    environ["QBPM_PROFILE_DIR"] = str(tmp_path)
    (tmp_path / "config.py").touch()
    config_file = tmp_path / "config.toml"
    config_file.write_text(f'''config_py_template = ""
        desktop_file_directory="{tmp_path}"''')
    run("-P", str(tmp_path), "new", "-C", str(tmp_path), "test")
    assert not (tmp_path / "test.desktop").exists()
