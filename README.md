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
and closed independently. They're very useful!

## Use cases
 - Use a "work" profile to isolate your work logins from your personal ones.
   Especially important if you have a work account on Google or Github!
 - Project-based profiles. I have a "qpm" profile which has library
   documentation, qutebrowser config, CI results, issues and PRs, and everything
   I need to work on qpm.
 - Because web browsers are hideous monstrosities, qutebrowser leaks a little
   bit of memory. If you leave it open 24/7 that can become a lot.  I use
   profiles both to organize my browsing and to keep my number of open tabs
   down, especially on machines with less memory. Since profiles open and close
   very quickly and keep a persisent sesion, I can open sets of tabs when I need
   them and close them when I don't, knowing I won't lose them.

## Usage
```
# create and launch a new profile called "finance" in $XDG_DATA_HOME/qutebrowser-profiles:
$ qpm new finance --launch
# or
$ qpm launch finance

# convert the contents of a window into a new profile:
# in qutebrowser, run: "session-save -o profile-name"
$ qpm from-session profile-name

# you can store profiles anywhere:
$ qpm --profile-dir ~/dev/my-project new project-info
$ cd ~/dev/my-project
$ qpm --profile-dir . launch project-info
# or
$ qutebrowser --basedir profile-name

# launch passes arguments it doesn't recognize to qutebrowser:
$ qpm launch python docs.python.org --target window --loglevel info
# is functionally equivalent to:
$ qutebrowser --basedir $XDG_DATA_HOME/qutebrowser-profiles/python docs.python.org --target window --loglevel info
```

## Disclaimer
This is alpha-quality software. Even though it doesn't do anything particularly
dangerous to the filesystem, there is always the risk that it will mangle your
data.

## Future work
- More shared config and data (configurable)
- Generated binaries and `.desktop` files
- Delete profiles?
- Use any profile as a base for new profiles (currently only the main config in
  `$XDG_CONFIG_HOME` is supported)
- Source `autoconfig.yml` instead of `config.py`
- Customizable config sourcing for those who like to split their config into
  multiple files
- Bundled config file optimized for single-site browsing
- `qpm.conf` to configure the features above
- Someday: qutebrowser plugin

## Known limitations
- If your config relies on `config.configdir` to dynamically source other config
  files (I may be the only person who does this), those config files will not be
  present in `qpm`-created profiles There are plenty of workarounds, such as
  hardcoding your main config dir instead of using `config.configdir`.
