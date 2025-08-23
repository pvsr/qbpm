from pathlib import Path

from qbpm import profiles
from qbpm.config import Config
from qbpm.profiles import Profile

from . import no_homedir_fixture  # noqa: F401


def check_is_empty(path: Path):
    assert len(list(path.iterdir())) == 0


def check_empty_profile(profile: Profile | None):
    assert profile
    config_dir = profile.root / "config"
    assert list(profile.root.iterdir()) == [config_dir]
    assert list(config_dir.iterdir()) == []


def check_new_profile(profile: Profile):
    assert profile
    config_dir = profile.root / "config"
    assert list(profile.root.iterdir()) == [config_dir]
    assert list(config_dir.iterdir()) == [config_dir / "config.py"]


def test_set_profile(tmp_path: Path):
    assert Profile("test", tmp_path).root == tmp_path / "test"


def test_create_profile(tmp_path: Path):
    profile = Profile("test", tmp_path)
    assert profiles.create_profile(profile)
    assert list(tmp_path.iterdir()) == [profile.root]
    check_empty_profile(profile)


def test_create_profile_conflict(tmp_path: Path):
    (tmp_path / "test").touch()
    profile = Profile("test", tmp_path)
    assert not profiles.create_profile(profile)


def test_create_profile_parent(tmp_path: Path):
    profile = Profile("../test", tmp_path / "profiles")
    assert not profiles.create_profile(profile)
    assert not (tmp_path / "test").exists()


def test_create_profile_nested_conflict(tmp_path: Path):
    assert profiles.create_profile(Profile("test", tmp_path))
    assert not profiles.create_profile(Profile("test/a", tmp_path))


def test_create_config(tmp_path: Path):
    (tmp_path / "config.py").touch()
    profile = Profile("test", tmp_path)
    config_dir = profile.root / "config"
    config_dir.mkdir(parents=True)
    profiles.create_config(profile, tmp_path, "{source_config_py}")
    config = config_dir / "config.py"
    assert list(config_dir.iterdir()) == [config]
    assert str(tmp_path / "config.py") in config.read_text()


def test_overwrite_config(tmp_path: Path):
    (tmp_path / "config.py").touch()
    profile = Profile("test", tmp_path)
    url = "http://example.com"
    config_dir = profile.root / "config"
    config_dir.mkdir(parents=True)
    config = config_dir / "config.py"
    backup = config_dir / "config.py.bak"
    profiles.create_config(profile, tmp_path, "")
    profiles.create_config(profile, tmp_path, "", url, True)
    assert set(config_dir.iterdir()) == {config, backup}
    assert url in config.read_text()
    assert url not in backup.read_text()


def test_link_autoconfig(tmp_path: Path):
    profile = Profile("test", tmp_path)
    config_dir = profile.root / "config"
    config_dir.mkdir(parents=True)
    (tmp_path / "autoconfig.yml").touch()
    profiles.link_autoconfig(profile, tmp_path, False)
    config = config_dir / "autoconfig.yml"
    assert list(config_dir.iterdir()) == [config]
    assert config.resolve().parent == tmp_path


def test_autoconfig_present(tmp_path: Path):
    profile = Profile("test", tmp_path)
    config_dir = profile.root / "config"
    config_dir.mkdir(parents=True)
    (tmp_path / "autoconfig.yml").touch()
    profiles.link_autoconfig(profile, tmp_path, False)
    profiles.link_autoconfig(profile, tmp_path, False)
    config = config_dir / "autoconfig.yml"
    assert list(config_dir.iterdir()) == [config]
    assert config.resolve().parent == tmp_path


def test_overwrite_autoconfig(tmp_path: Path):
    profile = Profile("test", tmp_path)
    config_dir = profile.root / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "autoconfig.yml").touch()
    (tmp_path / "autoconfig.yml").touch()
    profiles.link_autoconfig(profile, tmp_path, True)
    config = config_dir / "autoconfig.yml"
    assert set(config_dir.iterdir()) == {config, config_dir / "autoconfig.yml.bak"}
    assert config.resolve().parent == tmp_path


def test_new_profile(tmp_path: Path):
    (tmp_path / "config.py").touch()
    profile = Profile("test", tmp_path / "test")
    config = Config.load(None)
    config.qutebrowser_config_directory = tmp_path
    config.generate_desktop_file = False
    assert profiles.new_profile(profile, config)
    check_new_profile(profile)


def test_new_profile_autoconfig(tmp_path: Path):
    (tmp_path / "autoconfig.yml").touch()
    profile = Profile("test", tmp_path / "test")
    config = Config.load(None)
    config.qutebrowser_config_directory = tmp_path
    config.generate_desktop_file = False
    config.symlink_autoconfig = True
    profiles.new_profile(profile, config)
    config_dir = profile.root / "config"
    assert set(config_dir.iterdir()) == {config_dir / "autoconfig.yml"}


def test_new_profile_both(tmp_path: Path):
    (tmp_path / "config.py").touch()
    (tmp_path / "autoconfig.yml").touch()
    profile = Profile("test", tmp_path / "test")
    config = Config.load(None)
    config.qutebrowser_config_directory = tmp_path
    config.generate_desktop_file = False
    config.symlink_autoconfig = True
    profiles.new_profile(profile, config)
    assert len(set((profile.root / "config").iterdir())) == 2  # noqa: PLR2004


def test_config_template(tmp_path: Path):
    (tmp_path / "config.py").touch()
    profile = Profile("test", tmp_path)
    config_dir = profile.root / "config"
    config_dir.mkdir(parents=True)
    template = "# Profile: {profile_name}\nconfig.source('{source_config_py}')"
    profiles.create_profile(profile)
    profiles.create_config(profile, tmp_path, template)
    config_content = (profile.root / "config" / "config.py").read_text()
    assert "# Profile: test" in config_content
    assert f"config.source('{tmp_path / 'config.py'}')" in config_content


def test_missing_qb_config(tmp_path: Path):
    profile = Profile("test", tmp_path / "test")
    config = Config.load(None)
    config.qutebrowser_config_directory = tmp_path
    config.generate_desktop_file = False
    assert not profiles.new_profile(profile, config)
    config.qutebrowser_config_directory = tmp_path / "nonexistent"
    assert not profiles.new_profile(profile, config)
