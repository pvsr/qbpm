qbpm(1)

# NAME

qbpm - qutebrowser profile manager

# SYNOPSIS

*qbpm* [--profile-dir=<path>|-P <path>] <command> [<args>]

# DESCRIPTION

qbpm is a tool for creating, managing, and running qutebrowser profiles. Profile support
isn't built in to qutebrowser, at least not directly, but it does have a \--basedir flag
which allows qutebrowser to use any directory as the location of its config and
data and effectively act as a profile. qbpm creates profiles that source your
main qutebrowser config.py, but have their own separate autoconfig.yml, bookmarks, cookies,
history, and other data. Profiles can be run by starting qutebrowser with the
appropriate \--basedir, or more conveniently using the qbpm launch and qbpm choose commands.

# OPTIONS

*-h, --help*
	Show help message and quit.

*--version*
	Show version information and quit.

*-P, --profile-dir* <path>
	Use _path_ as the profile directory instead of the default location. Takes
	precedence over the QBPM_PROFILE_DIR environment variable.

*-C, --config-dir*
	Source config files from the provided directory instead of the global
	qutebrowser config location.

# COMMANDS

*new* [options] <profile> [<url>]
	Create a new qutebrowser profile named _profile_. If _url_ is present it will
	be used as the profile's home page.

	Options:

	*-l, --launch*
		Launch the profile after it is created.

	*-f, --foreground*
		If --launch is set, run qutebrowser in the foreground.

	*--no-desktop-file*
		Do not generate an XDG desktop entry for the profile. Always true on
		non-linux systems. See https://wiki.archlinux.org/title/Desktop_entries
		for information on desktop entries.

	*--overwrite*
		By default qbpm will refuse to create a profile if one with the same name
		already exists. --overwrite disables this check and replaces the existing
		profile's configuration files. Profile data is left untouched.

*launch* [options] <profile> [argument...]
	Start qutebrowser with --basedir set to the location of _profile_. All
	arguments following _profile_ will be passed on to qutebrowser.

	Options:

	*-f, --foreground*
		Run qutebrowser in the foreground instead of forking off a new process.

	*-c, --create*
		Create the profile if it does not exist.

	Examples:

		```
		\# launch my profile called work and open internal.mycompany.com
		qbpm launch work internal.mycompany.com

		\# launch a new profile called qb-dev, passing the flags to qutebrowser
		qbpm launch -n qb-dev --debug --json-logging
		```

*choose* [options]
	Open a menu to choose a qutebrowser profile to launch. On linux this defaults
	to dmenu or another compatible menu program such as rofi, and on macOS this
	will be an applescript dialog.

	*-m, --menu* <menu>
		Use _menu_ instead of the default menu program. This may be the name of a
		program on $PATH or a path to a program, in which case it will be run in
		dmenu mode if qbpm knows about the program, or a full command line.

	Examples:

		```
		\# runs "echo {profiles} | /path/to/rofi -dmenu -no-custom -p qutebrowser"
		qbpm choose -m /path/to/rofi

		qbpm choose -m "my-cool-menu --dmenu-mode --prompt qutebrowser"
		```

*from-session* [options] <session> [<name>]
	Create a new qutebrowser profile from _session_, which may either be the name
	of a session in the default qutebrowser data directory, or a path to a session
	file. By default the new profile will be named after _session_, but a custom
	profile name can be set via the _name_ argument. Supports the same options as
	*new*.

*desktop* <profile>
	Generate an XDG desktop entry for _profile_.

*edit* <profile>
	Open _profile_'s config.py in your default editor.

*list*
	List qutebrowser profiles.

# AUTHOR

Peter Rice

Contribute at https://github.com/pvsr/qbpm
