# qutebrowser profile manager

[![builds.sr.ht status](https://builds.sr.ht/~pvsr/qbpm/commits/main.svg)](https://builds.sr.ht/~pvsr/qbpm/commits/main?)

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
Create a new profile called "python", edit its `config.py`, then launch it:
```
$ qbpm new python
$ qbpm edit python
$ qbpm launch python docs.python.org
$ qbpm choose # run dmenu or another launcher to pick a profile
```

`qbpm from-session` can copy the tabs of a [saved qutebrowser
session](https://qutebrowser.org/doc/help/commands.html#session-save) to a new
profile. If you have a window full of tabs related to planning a vacation, you
could save it to a session called "vacation" using `:session-save -o vacation`
in qutebrowser, then create a new profile with those tabs:
```
$ qbpm from-session vacation
```

The default profile directory is `$XDG_DATA_HOME/qutebrowser-profiles`, where
`$XDG_DATA_HOME` is usually `~/.local/share`, but you can create and launch
profiles from anywhere using `--profile-dir`/`-P`:
```
$ qbpm --profile-dir ~/dev/my-project new qb-profile
$ cd ~/dev/my-project
$ qbpm -P . launch qb-profile
# or
$ qutebrowser --basedir qb-profile
```

## Installation
If you use Nix, you can install or run qbpm as a [Nix flake](https://nixos.wiki/wiki/Flakes).
For example, to run qbpm without installing it you can use `nix run github:pvsr/qbpm -- new my-profile`.

On Arch and derivatives, you can install the AUR package: [qbpm-git](https://aur.archlinux.org/packages/qbpm-git).

Otherwise you'll need to install from source, directly or using a tool like [uv](https://docs.astral.sh/uv/guides/tools/).
Using uv you can run qbpm without installing it using
`uv tool run --with git+https://github.com/pvsr/qbpm qbpm`, or install to `~/.local/bin` with
`uv tool install --with git+https://github.com/pvsr/qbpm qbpm`.
The downside of a source installation is that the [man page](https://github.com/pvsr/qbpm/blob/main/qbpm.1.scd)
and shell completions will not be installed automatically.

On Linux you can copy [`contrib/qbpm.desktop`](https://raw.githubusercontent.com/pvsr/qbpm/main/contrib/qbpm.desktop)
to `~/.local/share/applications` to create a qbpm desktop application that runs
`qbpm choose`.

### MacOS

Nix and uv will install qbpm as a command-line application, but if you want a
native Mac application you can clone this repository or copy the contents of
[`contrib/qbpm.platypus`](https://raw.githubusercontent.com/pvsr/qbpm/main/contrib/qbpm.platypus)
to a local file, install [platypus](https://sveinbjorn.org/platypus),
and create a qbpm app by running `platypus -P qbpm.platypus /Applications/qbpm.app`.
That will also make qbpm available as a default browser in `System Preferences > General > Default web browser`.

Note that there is currently [a qutebrowser bug](https://github.com/qutebrowser/qutebrowser/issues/3719)
that results in unnecessary `file:///*` tabs being opened.
