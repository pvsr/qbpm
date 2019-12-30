# `qpm`, a Qutebrowser Profile Manager

[![builds.sr.ht status](https://builds.sr.ht/~pvsr/qpm.svg)](https://builds.sr.ht/~pvsr/qpm?)

[Qutebrowser](https://github.com/qutebrowser/qutebrowser) is the best web
browser out there, but it doesn't handle huge numbers of open tabs very well
when it comes to memory usage and UI. I even found myself restarting qutebrowser
in order to free up memory pretty often. This is a tool I wrote to make it
easier to split my many, many open tabs between separate qutebrowser instances,
all sharing the same config file.

## Disclaimer
This is alpha-quality software with no test suite and minimal manual testing.
Even though it doesn't do anything too dangerous to the filesystem, there is
always the risk that it will delete or mangle your data.

## Examples

To create and launch a new profile called "finance" in
`$XDG_DATA_HOME/qutebrowser-profiles`, simply run:
```bash
qpm new finance --launch
# or
qpm launch finance
```

If you want to convert the contents of a window into a new profile, run
`session-save -o profile-name` in qutebrowser to create a session file for just
the active window, then run:
```bash
qpm from-session profile-name
```

I find it helpful to have a dedicated profile for each of my programming
projects, so I keep a profile in the project dir.
```bash
qpm -P ~/dev/qpm new profile
qpm -P ~/dev/qpm launch profile
```

## Future work
- Config file for default profile directory and more
- More shared config and data (configurable)
- Generated binaries and `.desktop` files
- The ability to delete profiles (need tests first!)
- Use any profile as a base for new profiles (currently only the main profile in
  `$XDG_CONFIG_HOME` is supported)
- Source `autoconfig.yml` instead of `config.py`
- Customizable config sourcing for those who like to split their config into
  multiple files

## Known limitations
- If your config relies on `config.configdir` to dynamically source other config
  files (I may be the only person who does this), `qpm`-created profiles may not
  result in exactly the same configuration as your main profile. There are
  plenty of workarounds, such as hardcoding your main config dir instead of
  using `config.configdir`.
