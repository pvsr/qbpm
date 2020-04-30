# `qpm`: qutebrowser profile manager

[![builds.sr.ht status](https://builds.sr.ht/~pvsr/qpm.svg)](https://builds.sr.ht/~pvsr/qpm?)

[qutebrowser](https://github.com/qutebrowser/qutebrowser) is a web browser with
vim-like keybindings. It's great! qpm is a tool for managing qutebrowser
profiles. qutebrowser "profiles" are actually independent qutebrowser base
directories, each with their own cache, config, and storage. qutebrowser can be
configured to use these profiles instead of its normal config and data
directories using the `--basedir` flag.  qpm makes it easy to create qutebrowser
profiles, from scratch or as copies of your main profile, and to run these
profiles as independent, persistent, qutebrowser sessions.

## Use cases
 - Use a "work" profile to isolate your work logins from your personal ones.
   Especially important if you have a work account on Google or Github!
 - Project-based profiles. I have a "qpm" profile which has library
   documentation, qutebrowser config, CI results, issues and PRs, and everything
   I need to work on qpm.
 - So qutebrowser is great, but if you leave a lot of tabs open 24/7 you might
   notice that qutebrowser leaks a little bit of memory.  I use profiles both to
   organize my browsing and keep the number of open tabs and memory usage low.
   Since profiles are very quick to stop and start I open tabs when I need them
   and I close them when I don't, and I know I won't lose them.

## Usage
```
# create and launch a new profile called "finance" in $XDG_DATA_HOME/qutebrowser-profiles
$ qpm new finance --launch
# or
$ qpm launch finance

# convert the contents of a window into a new profile
# in qutebrowser, run: "session-save -o profile-name"
$ qpm from-session profile-name

# you can keep profiles anywhere, such as project dirs
$ qpm -P ~/dev/qpm new profile-name
$ cd ~/dev/qpm
$ qpm -P . launch profile-name

# arguments that qpm doesn't recognize will be passed to qutebrowser
$ qpm launch python docs.python.org --target window --loglevel info
# is functionally equivalent to:
$ qutebrowser -B ~/$XDG_DATA_HOME/qutebrowser-profiles/python docs.python.org --target window --loglevel info
```

## Disclaimer
This is alpha-quality software. Even though it doesn't do anything particularly
dangerous to the filesystem, there is always the risk that it will mangle your
data.

## Future work
- More shared config and data (configurable)
- Generated binaries and `.desktop` files
- The ability to delete profiles (need tests first!)
- Use any profile as a base for new profiles (currently only the main profile in
  `$XDG_CONFIG_HOME` is supported)
- Source `autoconfig.yml` instead of `config.py`
- Customizable config sourcing for those who like to split their config into
  multiple files
- Bundled config file optimized for single-site browsing
- `qpm.conf` to configure the features above

## Known limitations
- If your config relies on `config.configdir` to dynamically source other config
  files (I may be the only person who does this), those config files will not be
  present in `qpm`-created profiles There are plenty of workarounds, such as
  hardcoding your main config dir instead of using `config.configdir`.
