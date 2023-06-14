Configuration Command
========================================================================================================================
The `config` command can be used to get and set the configuration options used by `b`.

Config settings are not stored in the project and a global to all instances of `b` used on a system.  Config files are stored in the user config directory which is set using the `apprdirs` Python module.  On Windows, that pay might be:

    C:\Users\<your-username>\AppData\Roaming\exsystems\b\settings.cfg

It is possibly, but not recommended, to modify this settings file directly.



Listing Config Options
------------------------------------------------------------------------------------------------------------------------
To get a list of all of the available settings and their current values run:

    $ b config

Example output might look like this:

    general.editor=notepad
    general.dir=.bugs
    general.user=Default <default.user@example.com>



Get Config Setting
------------------------------------------------------------------------------------------------------------------------
To get the current value of a specific config setting, such as the "editor", specify it's name after the config command, for example:

    $ b config editor

Which might output something like:

    editor = notepad



Change Config Setting
------------------------------------------------------------------------------------------------------------------------
To change a setting, append the key and new value after the `config` command.  For example, to change the editor to VS Code, run:

    $ b config editor code
