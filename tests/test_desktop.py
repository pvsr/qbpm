from pathlib import Path

from qbpm import Profile
from qbpm.desktop import create_desktop_file

TEST_DIR = Path(__file__).resolve().parent


def test_create_desktop_file(tmp_path: Path):
    application_path = tmp_path / "applications"
    application_path.mkdir()
    profile = Profile("test", tmp_path)
    create_desktop_file(profile, application_path)
    assert (application_path / "test.desktop").read_text() == (
        TEST_DIR / "test.desktop"
    ).read_text().replace("{qbpm}", " ".join(profile.cmdline()))
