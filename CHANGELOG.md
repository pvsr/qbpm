# next
  - built in support for more wayland menus:
    - walker
    - tofi
    - wmenu

# 1.0rc3
  - breaking: stop sourcing files from `~/.config/qutebrowser/conf.d/`
    - this was undocumented, nonstandard, and didn't work as well as it could
  - switch to `pyproject.toml`
  - hopefully use the right qutebrowser dirs on Windows
  - `choose`: add `qutebrowser` menu item for the main qutebrowser profile
  - added `-C` argument to support referencing qutebrowser configs other than the one in ~/.config
  - added `click`-generated completions for bash and zsh
  - added option support to fish completions
  - removed `--create` from `qbpm launch`
  - make generated `.desktop` files match qutebrowser's more closely

# 1.0rc2:
  - `choose`: builtin support for `fzf` and `fuzzel`
  - moved argument handling to click
  - `qbpm launch`'s `-n`/`--new` renamed to `-c`/`--create`
