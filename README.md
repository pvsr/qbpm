# `qpm`: Qutebrowser Profile Manager

[![builds.sr.ht status](https://builds.sr.ht/~pvsr/qpm.svg)](https://builds.sr.ht/~pvsr/qpm?)

[Qutebrowser](https://github.com/qutebrowser/qutebrowser) is by farthe best web
browser available, but if you're the type of person who accumulates a huge
number of open tabs, you'll quickly notice two deficiencies: the tab bar becomes
a lot less useful once it starts to overflow horizontally, and memory usage gets
a bit out of control if you leave the browser open 24/7; I even find myself
restarting qutebrowser to free up memory from time to time on machines with less
RAM.  Unfortunately I've also noticed poor performance with multiple windows
open<sup>[1](#footnote1)</sup>, which is annoying on its own and also means I
can't split my tabs between multiple windows to improve the tab bar experience.
So, inspired by qutebrowser's idea of sessions and Firefox's profile manager, I
wrote `qpm` in order to better organize my mess of tabs by dividing them between
separate qutebrowser instances, all sharing the same config file.

<a name="footnote1">1</a>: For the record, based on other issues in the past I
suspect this is a rendering bug in QtWebEngine, not qutebrowser itself.

## Examples

To create and launch a new profile called "finance" in
`$XDG_DATA_HOME/qutebrowser-profiles`, simply run:
`qpm new finance --launch` or `qpm launch finance`

If you want to convert the contents of a window into a new profile, run
`session-save -o profile-name` in qutebrowser to create a session file for just
the active window, then run: `qpm from-session profile-name`

I find it helpful to have a dedicated profile for each of my programming
projects, so I keep a profile in the project dir, using:
`qpm -P ~/dev/qpm new profile` and `qpm -P ~/dev/qpm launch profile`

Arguments that `qpm` doesn't recognize will be passed to qutebrowser, so you can
do stuff like:
`qpm launch python docs.python.org --target window --loglevel info`

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
