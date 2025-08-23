# 2.0
## config
qbpm now reads configuration options from a `$XDG_CONFIG_HOME/qbpm/config.toml`!
  - to install the default config file:
    - run `qbpm config path` and confirm that it prints out a path
    - run `qbpm config default > "$(qbpm config path)"`
  - supported configuration options:
    - `config_py_template`: control the contents of `config.py` in new profiles
    - `symlink_autoconfig`: symlink qutebrowser's `autoconfig.yml` in new profiles
    - `profile_directory` and `qutebrowser_config_directory`
      - equivalent `--profile-dir` to `--qutebrowser-config-dir` 
    - `generate_desktop_file` and `desktop_file_directory`
      - whether to generate an XDG desktop entry for the profile and where to put it
    - `menu`: equivalent to `--menu` for `qbpm choose`
    - `menu_prompt`: prompt shown in most menus
    - see default config file for more detailed documentation

## other
  - support for symlinking `autoconfig.yml` in addition to or instead of sourcing `config.py`
  - `qbpm new --overwrite`: back up existing config files by moving to e.g. `config.py.bak`
  - `contrib/qbpm.desktop`: add `MimeType` and `Keywords`, fix incorrect formatting of `Categories`
  - allow help text to be slightly wider to avoid awkward line breaks
  - macOS: fix detection of qutebrowser binary in /Applications

# 1.0rc4
  - `choose`: support `walker`, `tofi`, and `wmenu`
  - better detection of invalid/nonexistent profiles

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
  - `choose`: support `fzf` and `fuzzel`
  - use `click `for CLI parsing
  - `qbpm launch`'s `-n`/`--new` renamed to `-c`/`--create`
  - expand fish shell completions

# 1.0rc1:
  - add a man page

# 0.6
  - better error handling

# 0.5
  - `choose`: support custom menu command
  - `choose`: support `dmenu-wl` and `wofi`

# 0.4
  - `choose` subcommand (thanks, @mtoohey31!)
  - load autoconfig.yml by default
  - shell completions for fish
