from os import environ
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def no_homedir_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    environ["XDG_CONFIG_HOME"] = str(tmp_path)
    environ["XDG_DATA_HOME"] = str(tmp_path)
    monkeypatch.setattr("qbpm.paths.get_app_dir", lambda *_args, **_kwargs: tmp_path)
    monkeypatch.setattr("qbpm.paths.Path.home", lambda: tmp_path)
