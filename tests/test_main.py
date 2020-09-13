from os import environ
from pathlib import Path

import pytest  # type: ignore

from qpm.main import main


def test_profile_dir_option(tmp_path: Path):
    main(["-P", str(tmp_path), "new", "test"])
    assert list(tmp_path.iterdir()) == [tmp_path / "test"]


def test_profile_dir_env(tmp_path: Path):
    environ["QPM_PROFILE_DIR"] = str(tmp_path)
    main(["new", "test"])
    assert list(tmp_path.iterdir()) == [tmp_path / "test"]


@pytest.mark.skip(reason="need to allow path of session")
def test_from_session(tmp_path: Path):
    environ["QPM_PROFILE_DIR"] = str(tmp_path)
    session = tmp_path / "test.yml"
    # TODO file contents
    main(["from-session", str(session)])
    assert list(tmp_path.iterdir()) == [tmp_path / "test"]
