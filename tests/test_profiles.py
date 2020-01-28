from pathlib import Path

from qpm import config, profiles, operations

def check_is_empty(path: Path):
    assert len(list(path.iterdir())) == 0

def check_empty_profile(profile: Path):
    assert profile
    config_dir = profile / "config"
    assert list(profile.iterdir()) == [config_dir]
    assert list(config_dir.iterdir()) == []

def check_new_profile(profile: Path):
    assert profile
    config_dir = profile / "config"
    assert list(profile.iterdir()) == [config_dir]
    assert list(config_dir.iterdir()) == [config_dir / "config.py"]

def test_set_profile(tmp_path: Path):
    config.profiles_dir = tmp_path
    assert profiles.get_profile_root("test") == tmp_path / "test"

def test_get_profile_path(tmp_path: Path):
    config.profiles_dir = tmp_path
    assert profiles.get_profile_root(tmp_path) == tmp_path

def test_create_profile(tmp_path: Path):
    config.profiles_dir = tmp_path
    profile = profiles.create_profile("test")
    assert profile
    assert list(tmp_path.iterdir()) == [profile]
    check_empty_profile(profile)

def test_create_profile_path(tmp_path: Path):
    config.profiles_dir = tmp_path
    profile = profiles.create_profile(tmp_path / "test")
    assert profile
    assert list(tmp_path.iterdir()) == [profile]
    check_empty_profile(profile)

def test_create_profile_conflict(tmp_path: Path):
    config.profiles_dir = tmp_path
    (tmp_path / "test").touch()
    profile = profiles.create_profile("test")
    assert not profile

def test_create_profile_parent(tmp_path: Path):
    config.profiles_dir = tmp_path / "profiles"
    profile = profiles.create_profile("../test")
    assert not (tmp_path / "test").exists()

def test_create_profile_nested_conflict(tmp_path: Path):
    config.profiles_dir = tmp_path
    assert profiles.create_profile("test")
    assert not profiles.create_profile("test/a")

def test_create_config(tmp_path: Path):
    config.profiles_dir = tmp_path
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    profiles.create_config(tmp_path)
    assert list(config_dir.iterdir()) == [config_dir / "config.py"]

def test_ensure_profile_exists_exists(tmp_path: Path):
    config.profiles_dir = tmp_path
    profile = tmp_path / "test"
    profile.mkdir()
    assert profiles.ensure_profile_exists("test", False) == profile
    assert profiles.ensure_profile_exists("test", True) == profile
    assert profiles.ensure_profile_exists(profile, False) == profile
    assert profiles.ensure_profile_exists(profile, True) == profile
    check_is_empty(profile)

def test_ensure_profile_exists_does_not_exist(tmp_path: Path):
    config.profiles_dir = tmp_path
    profile = tmp_path / "test"
    assert not profiles.ensure_profile_exists("test", False)
    assert not profiles.ensure_profile_exists(profile, False)
    check_is_empty(tmp_path)

def test_ensure_profile_exists_not_dir(tmp_path: Path):
    config.profiles_dir = tmp_path
    profile = tmp_path / "test"
    profile.touch()
    assert not profiles.ensure_profile_exists("test", False)
    assert not profiles.ensure_profile_exists(profile, False)
    assert not profiles.ensure_profile_exists("test", True)
    assert not profiles.ensure_profile_exists(profile, True)

def test_ensure_profile_exists_create(tmp_path: Path):
    config.profiles_dir = tmp_path
    profile = tmp_path / "test"
    assert profiles.ensure_profile_exists("test", True) == profile
    check_new_profile(profile)

def test_ensure_profile_exists_create_path(tmp_path: Path):
    config.profiles_dir = tmp_path
    profile = tmp_path / "test"
    assert profiles.ensure_profile_exists(profile, True) == profile
    check_new_profile(profile)

def test_new_profile(tmp_path: Path):
    config.profiles_dir = tmp_path
    profile = tmp_path / "test"
    assert profiles.new_profile("test") == profile
    check_new_profile(profile)

def test_new_profile_path(tmp_path: Path):
    config.profiles_dir = tmp_path
    profile = tmp_path / "test"
    assert profiles.ensure_profile_exists(profile) == profile
    check_new_profile(profile)
