Using `b`
========================================================================================================================
Commands have been grouped by functionality.  For help with individual commands, please see their respective sections below.

- [Editing Commands](editing.md) - `add`, `rename`, `assign`, `edit`, `comment`, `resolve`, `reopen`.
- [Read-Only Commands](read-only.md) - `list`, `details`, `users`, `id`
- [Configuration](config.md) - `config`
- [Templates](templates.md) - `templates`
- [System](system.md) - `init`, `version`, `verify`, `migrate`




Additional Help
------------------------------------------------------------------------------------------------------------------------
All `b` commands take the form `b COMMAND [OPTIONS] [ARGUMENTS]`.  You can see a full list and command signatures by running `b --help`.

    init                initialize a bugs directory for new bugs
    add                 adds a new open bug to the database
    rename              rename the bug denoted by PREFIX to TEXT
    users               display a list of all users and the number of open bugs assigned to each
    assign              assign bug denoted by PREFIX to username
    details             print the extended details of the specified bug
    edit                launch the system editor to provide additional details
    comment             append the provided comment to the details of the bug
    resolve             mark the specified bug as resolved
    reopen              mark the specified bug as open
    list                list all bugs according to the specified filters
    id                  given a prefix return the full ID of a bug
    verify              run through each bug YAML file and validate it against schema, reporting errors
    templates           list templates available when creating new bug reports
    config              adjust configurations - default lists all
    migrate             migrate bugs directory to the latest version
    version             output the version number of b and exit

Similarly, additional help for each command can be solicited by issuing `b COMMAND --help`.  For example, `b list --help` shows:

    Usage: b list [-h] [-r] [-o OWNER] [-g GREP] [-a | -c]

    Options:
    -h, --help            show this help message and exit
    -r, --resolved        include resolved bugs
    -o, --owner OWNER     "*" lists all, "nobody" lists unassigned, otherwise text to matched against username
    -g, --grep GREP       filter by the search string appearing in the title
    -a, --alpha           list bugs alphabetically
    -c, --chrono          list bugs chronologically




Output Verbosity
------------------------------------------------------------------------------------------------------------------------
To increase the verbosity of the tool and report more information about what is happening internally, use the `-v` flag.

The `-v` flag is unique in that it must be place **before** the command.  For example,

    $ b -v verify

This will print INFO level logging output.  To increase the verbosity further, add another 'v':

    $ b -vv verify

Which will switch to printing DEBUG level logging information.  This is as verbose as `b` will get.

The verbose switch is compatible with all `b` commands, however, not every command has verbose details to print.
