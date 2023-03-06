from os import environ
from pathlib import Path

from click.testing import CliRunner

from qbpm.main import main


def test_profile_dir_option(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(main, ["-P", str(tmp_path), "new", "test"])
    assert result.exit_code == 0
    assert result.output.strip() == str(tmp_path / "test")
    assert list(tmp_path.iterdir()) == [tmp_path / "test"]


def test_profile_dir_env(tmp_path: Path):
    environ["QBPM_PROFILE_DIR"] = str(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["new", "test"])
    assert result.exit_code == 0
    assert result.output.strip() == str(tmp_path / "test")
    assert list(tmp_path.iterdir()) == [tmp_path / "test"]


def test_from_session(tmp_path: Path):
    environ["QBPM_PROFILE_DIR"] = str(tmp_path)
    session = tmp_path / "test.yml"
    session.touch()
    runner = CliRunner()
    result = runner.invoke(main, ["from-session", str(session)])
    assert result.exit_code == 0
    assert result.output.strip() == str(tmp_path / "test")
    assert set(tmp_path.iterdir()) == {session, tmp_path / "test"}
