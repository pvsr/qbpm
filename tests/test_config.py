from pathlib import Path

import pytest
from dacite import MissingValueError

from qbpm.config import load_config

# def test_config_none():
#     config = load_config(None)
#     assert config is not None


def test_nonexistent_config(tmp_path: Path):
    assert load_config(tmp_path) is None
    assert load_config(tmp_path / "config.toml") is None


def test_empty_config(tmp_path: Path):
    file = tmp_path / "config.toml"
    file.touch()
    with pytest.raises(MissingValueError, match="config_py_template"):
        load_config(file)


def test_minimal_config(tmp_path: Path):
    file = tmp_path / "config.toml"
    file.write_text("""config_py_template = 'invalid'""")
    config = load_config(file)
    assert config is not None
    # breakpoint()
    assert (
        config.profile_directory
        == Path("~/.local/share/qutebrowser-profiles").expanduser()
    )
    assert config.config_py_template == "invalid"


# def test_full_config(tmp_path: Path):
#     file = tmp_path / "config.toml"
#     file.write_text("""asdf
#     """)
#     config = load_config(file)
#     assert config is not None
