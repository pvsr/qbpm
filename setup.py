from setuptools import setup, find_packages

setup(
    name="qpm",
    version="0.1",
    packages=find_packages(),
    entry_points={"console_scripts": ["qpm = qpm.main:main"]},
    install_requires=["pyxdg"],
    author="Peter Rice",
    author_email="peter@peterrice.xyz",
    description="Qutebrowser profile manager",
)
