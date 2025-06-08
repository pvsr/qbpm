from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def no_homedir_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("qbpm.paths.default_qbpm_config_dir", lambda: tmp_path)
    monkeypatch.setattr("qbpm.paths.default_qbpm_application_dir", lambda: tmp_path)
    monkeypatch.setattr("qbpm.paths.default_profile_dir", lambda: tmp_path)
