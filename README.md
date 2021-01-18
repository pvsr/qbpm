# `qpm`: qutebrowser profile manager

[![builds.sr.ht status](https://builds.sr.ht/~pvsr/qpm.svg)](https://builds.sr.ht/~pvsr/qpm?)

[qutebrowser](https://github.com/qutebrowser/qutebrowser) is a web browser with
vim-like keybindings. It's great! qpm is a small tool for creating qutebrowser
"profiles", directories you can tell qutebrowser to store its config and data in
using the `--basedir` flag.  You can use qpm to create profiles that share
config with your standard qutebrowser installation and run them using the
`launch` subcommand, which wraps qutebrowser and points `--basedir` at your
profile directory. qutebrowser sessions started with different base directories
are entirely separate, have their own histories and sessions, and can be opened
and closed independently.

## Use cases
 - Use a "work" profile to isolate your work logins from your personal ones.
   Especially important if you have a work account on Google or Github!
 - Project-based profiles. I have a "qpm" profile which has library
   documentation, qutebrowser config, CI results, and everything I need to work
   on qpm.
 - Web browsers use a lot of memory and qutebrowser is no exception. I use
   profiles both to organize my browsing and to keep my number of open tabs
   under control, especially on machines with less memory. Since profiles open
   and close very quickly and keep a persisent session, I can open sets of tabs
   when I need them and close them when I don't, knowing I won't lose them.

## Usage
Create a new profile called "python", edit its `config.py`, then launch it:
```
$ qpm new python
$ qpm edit python
$ qpm launch python docs.python.org
```

Notice that `qpm launch` passes extra arguments directly to qutebrowser, so you
can use it to open urls in your profile and use any options you would pass to
qutebrowser:
```
$ qpm launch python duck.com --target window --loglevel info
```

`qpm from-session` can copy the tabs of a [saved qutebrowser
session](https://qutebrowser.org/doc/help/commands.html#session-save) to a new
profile. If you have a window full of tabs related to planning a vacation, you
could save it to a session called "vacation" using `:session-save -o vacation`
in qutebrowser, then create a new profile with those tabs:
```
$ qpm from-session vacation
```

The default profile directory is `$XDG_DATA_HOME/qutebrowser-profiles`, where
`$XDG_DATA_HOME` is usually `$HOME/.local/share`, but you can keep profiles
anywhere using `--profile-dir`/`-P`: 
```
$ qpm --profile-dir ~/dev/my-project new qb-profile
$ cd ~/dev/my-project
$ qpm -P . launch qb-profile
# or
$ qutebrowser --basedir qb-profile
```

## Future ideas that may or may not happen
- Edit flag and/or subcommand to edit the generated `config.py`
- Installation instructions
- More shared or copied config and data
- Use any profile as a base for new profiles (currently only the main config in
  `$XDG_CONFIG_HOME` is supported)
- Source `autoconfig.yml` instead of `config.py`
- Bundled config file optimized for single-site browsing
- `qpm.conf` to configure the features above
- Someday: qutebrowser plugin

Patches accepted!

## Known limitations
If your `config.py` relies on `config.configdir` to dynamically source other
config files ([like
this](https://github.com/pvsr/dotfiles/blob/34531d7be9e0c409be84ba8875c22c7e03a13b3d/qutebrowser/.config/qutebrowser/config.py#L97-L98)),
those config files will not be present in `qpm`-created profiles. There are
plenty of workarounds, such as hardcoding your main config dir instead of using
`config.configdir`.
