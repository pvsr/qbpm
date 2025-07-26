# qutebrowser profile manager

[![builds.sr.ht status](https://builds.sr.ht/~pvsr/qbpm/commits/main.svg)](https://builds.sr.ht/~pvsr/qbpm/commits/main?)
[![PyPI](http://img.shields.io/pypi/v/qbpm.svg)](https://pypi.python.org/pypi/qbpm)

qbpm (qutebrowser profile manager) is a tool for creating, managing, and running
[qutebrowser](https://github.com/qutebrowser/qutebrowser) profiles. Profile support
isn't built in to qutebrowser, at least not directly, but it does have a `--basedir` flag
which allows qutebrowser to use any directory as the location of its config and
data and effectively act as a profile. qbpm creates profiles that source your
main qutebrowser `config.py`, but have their own separate `autoconfig.yml`, bookmarks, cookies,
history, and other data. Profiles can be run by starting qutebrowser with the
appropriate `--basedir`, or more conveniently using the `qbpm launch` and `qbpm choose` commands.

qutebrowser shares session depending on the basedir, so launching the same
profile twice will result in two windows sharing a session, which means running
`:quit` in one will exit both and launching the profile again will reopen both
windows. But launching two distinct profiles will start two entirely separate
instances of qutebrowser which can be opened and closed independently.

## Usage
To create a new profile called "python" and launch it with the python docs open:
```
$ qbpm new python
$ qbpm launch python docs.python.org
```

Note that all arguments after `qbpm launch PROFILE` are passed to qutebrowser,
so options can be passed too: `qbpm launch python --target window pypi.org`.

If you have multiple profiles you can use `qbpm choose` to bring up a list of
profiles and select one to launch. Depending on what your system has available
the menu may be `dmenu`, `fuzzel`, `fzf`, an applescript dialog, or one of many
other menu programs qbpm can detect. Any dmenu-compatible menu can be used with
`--menu`, e.g. `qbpm choose --menu 'fuzzel --dmenu'`. As with `qbpm launch`,
extra arguments are passed to qutebrowser.

Run `qbpm --help` to see other available commands.

By default when you create a new profile a `.desktop` file is created that
launches the profile. This launcher does not depend on qbpm at all, so if you
want you can run `qbpm new` once and keep using the profile without needing
qbpm installed on your system.

## Installation
If you use Nix, you can install or run qbpm as a [Nix flake](https://nixos.wiki/wiki/Flakes).
For example, to run qbpm without installing it you can use `nix run github:pvsr/qbpm -- new my-profile`.

On Arch and derivatives, you can install the AUR package: [qbpm-git](https://aur.archlinux.org/packages/qbpm-git).

Otherwise you can install directly from PyPI using [uv](https://docs.astral.sh/uv/guides/tools/),
pip, or your preferred client. With uv it's `uv tool run qbpm` to run qbpm
without installing and `uv tool install qbpm` to install to `~/.local/bin`.
The downside of going through PyPI is that the [man page](https://github.com/pvsr/qbpm/blob/main/qbpm.1.scd)
and shell completions will not be installed automatically.

On Linux you can copy [`contrib/qbpm.desktop`](https://raw.githubusercontent.com/pvsr/qbpm/main/contrib/qbpm.desktop)
to `~/.local/share/applications` to create a qbpm desktop application that runs
`qbpm choose`.

### MacOS

Nix and uv will install qbpm as a command-line application, but if you want a
native Mac application you can download [`contrib/qbpm.platypus`](https://raw.githubusercontent.com/pvsr/qbpm/main/contrib/qbpm.platypus),
install [platypus](https://sveinbjorn.org/platypus), and create a qbpm app with
`platypus -P qbpm.platypus /Applications/qbpm.app`. That will also make qbpm
available as a default browser in `System Preferences > General > Default web browser`.

Note that there is currently [a qutebrowser bug](https://github.com/qutebrowser/qutebrowser/issues/3719)
that results in unnecessary `file:///*` tabs being opened.
