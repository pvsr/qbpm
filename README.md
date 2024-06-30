# qutebrowser profile manager

[![builds.sr.ht status](https://builds.sr.ht/~pvsr/qbpm.svg)](https://builds.sr.ht/~pvsr/qbpm?)

qutebrowser profile manager (qbpm) is a tool for creating and managing
[qutebrowser](https://github.com/qutebrowser/qutebrowser) profiles. There isn't
any built in concept of profiles in qutebrowser, but there is a `--basedir` flag
which allows qutebrowser to use any directory as the location of its config and
data and effectively act as a profile. qbpm creates profiles that source your
main qutebrowser `config.py`, but have their own separate `autoconfig.yml`, bookmarks, cookies,
history, and other data. It also acts as a wrapper around qutebrowser that sets
up `--basedir` for you, so you can treat `qbpm launch` as an alias for
`qutebrowser`, such as to open a url: `qbpm launch my-profile example.org`.

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
`$XDG_DATA_HOME` is usually `$HOME/.local/share`, but you can create and launch
profiles from anywhere using `--profile-dir`/`-P`:
```
$ qbpm --profile-dir ~/dev/my-project new qb-profile
$ cd ~/dev/my-project
$ qbpm -P . launch qb-profile
# or
$ qutebrowser --basedir qb-profile
```

## Installation
If you're on Arch, you can install the AUR package: [qbpm-git](https://aur.archlinux.org/packages/qbpm-git).
If you use [Nix](https://nixos.org/), qbpm is available as a flake, which
can be added as an input to your system flake or installed to your profile using
`nix profile install github:pvsr/qbpm`; there's also a standalone `default.nix`
file for use with `nix-env`.

For all other systems the best option is probably [pipx](https://pipx.pypa.io/stable/).
Using pipx you can run qbpm without installing by running
`pipx run --spec git+https://github.com/pvsr/qbpm.git qbpm`, and install it with
`pipx install git+https://github.com/pvsr/qbpm.git`.
If you're on Linux you can copy `contrib/qbpm.desktop` to
`~/.local/share/applications` to create a qbpm desktop application that runs
`qbpm choose`.

### MacOS

Nix and pipx will install qbpm as a command-line application, but if you want a
native Mac application too you can clone this repository or copy
`contrib/qbpm.platypus` to a local file, install [platypus](https://sveinbjorn.org/platypus),
and use it to create a qbpm app by running `platypus -P contrib/qbpm.platypus /Applications/qbpm.app`.
That will also make qbpm available to select as a default browser in `System Preferences > General > Default web browser`.
Note that there is currently [a qutebrowser bug](https://github.com/qutebrowser/qutebrowser/issues/3719)
that results in unnecessary `file:///*` tabs being opened.

## Future ideas that may or may not happen
- Release through github
- More shared or copied config and data
- Use any profile as a base for new profiles (currently only the main config in
  `$XDG_CONFIG_HOME` is supported)
- Source `autoconfig.yml` instead of `config.py`
- Bundled config file optimized for single-site browsing
- `qbpm.conf` to configure the features above
- Someday: qutebrowser plugin
