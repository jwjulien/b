System Commands
========================================================================================================================
The commands presented here don't really fit within the other command set files.  So they are referred to as "system" commands.



Init Command
------------------------------------------------------------------------------------------------------------------------
To get started using `b`, a `.bugs` directory must first be initialized.  To initialize a new .bugs directory in the current directory, typically the root of a project, run:

    $ b init

Then, from anywhere in the project (i.e. from the root directory or any subdirectory under the root) you can then interact with `b`.

For more help with setting up a new .bugs directory, please see the [[../getting_started]] guide.



Version Command
------------------------------------------------------------------------------------------------------------------------
The version command simply prints the installed version of b and exits.

    $ b version




Migrate Command
------------------------------------------------------------------------------------------------------------------------
If you have updated from an older version of `b`, then you might have a .bugs directory that doesn't match the current YAML format.  To migrate an existing set of bugs to the new format issue the `migrate` command:

    $ b migrate

This will transform the .bugs directory to the latest format making them compatible with the installed version of `b`.
