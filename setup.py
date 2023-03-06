from setuptools import find_packages, setup

setup(
    name="qbpm",
    version="0.6",
    url="https://github.com/pvsr/qbpm",
    packages=find_packages(),
    entry_points={"console_scripts": ["qbpm = qbpm.main:main"]},
    install_requires=["pyxdg"],
    author="Peter Rice",
    author_email="peter@peterrice.xyz",
    description="qutebrowser profile manager",
)
