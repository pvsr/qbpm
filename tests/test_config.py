from pathlib import Path

from qbpm.config import load_config

# def test_config_none():
#     config = load_config(None)
#     assert config is not None


def test_nonexistent_config(tmp_path: Path):
    assert load_config(tmp_path) is None
    assert load_config(tmp_path / "config.toml") is None


# def test_empty_config(tmp_path: Path):
#     file = tmp_path / "config.toml"
#     file.touch()
#     # raises
#     try:
#         config = load_config(file)
#     except Exception as e:
#         assert e is None
#     # TODO should be error
#     assert config is not None


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
