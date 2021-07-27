from setuptools import setup, find_packages

setup(
    name="qbpm",
    version="0.4",
    url="https://git.sr.ht/~pvsr/qpm",
    packages=find_packages(),
    entry_points={"console_scripts": ["qbpm = qpm.main:main"]},
    install_requires=["pyxdg"],
    author="Peter Rice",
    author_email="peter@peterrice.xyz",
    description="qutebrowser profile manager",
    use_scm_version={"write_to": "qpm/version.py"},
    setup_requires=["setuptools_scm"],
)
