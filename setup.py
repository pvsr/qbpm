from setuptools import setup

setup(
    name="qbpm",
    version="0.1",
    packages=["qbpm"],
    entry_points={"console_scripts": ["qbpm = qbpm.main:main"]},
    install_requires=["pyxdg"],
    author="Peter Rice",
    author_email="peter@peterrice.xyz",
    description="Qutebrowser profile manager",
)
