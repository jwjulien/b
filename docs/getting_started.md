Getting Stared Using `b`
========================================================================================================================
If you haven't already, start by [installing](installation) b on your system.  Once installed, the `b` command should be available at any command prompt on your system.  Verify that you have properly installed `b` by running:

    $ b version

You should see something like:

    b version 2.0.0

Though the version number will be different and should match the version that you installed.



Initialization
------------------------------------------------------------------------------------------------------------------------
Before `b` can be used, a .bugs directory must be created.  To do this, first open a command prompt and `cd` into the root directory of your project, or to whatever location you want tis new `.bugs` directory to reside in then run:

    $ b init

That's it.  Now if you run:

    $ b

You should see:

    Found 0 open bugs




Adding a new bug
------------------------------------------------------------------------------------------------------------------------
To add a new open bug to the database, run the following command:

    $ b add "A new bug"

To create a bug with a title "A new bug".  You should see output indicating the ID of the new bug, which should appear something like the following:

    Added bug 6:8dfaf05e72c8680e3f99bdf3cfdced988e95617



### Bug Prefixes #######################################################################################################
The "6" in the bug ID string above is called the *prefix*.  The remaining characters make up the rest of the bug's complete *ID*.

This *prefix* is what is used to work with the bug from this point forward.


> **_Warning:_** Prefixes are calculated, using the fewest leading characters of each bugs ID needed to uniquely identify the bug.  Because the bug IDs are randomly generated each time a new bug is added, this means that prefixes can and will change over time.
>
> For example, if a second bug were added after the example above, it's ID might be "65:10c6ede12420d157f1d794a0e3319f324b9b32" (note the two character prefix "65").  The prefix of the first bug would then become "68" rather than just "6".
>
> To see a list of open bugs (and their current prefixes), use the `b list` command.

There is no harm is using more characters than just the prefix to reference a bug, for example, both of these commands are equivalent:

    $ b resolve 6
    $ b resolve 68df

Either would change the "open" attribute to False for the bug that was just created with the `add` command above.



Listing Bugs
------------------------------------------------------------------------------------------------------------------------
To get a list of open bugs, run `b list`.  Or, for convenience, just `b` (the default command is `list` when not specified).

To see resolved bugs (where the `open` attribute has been set to False) use the `-r` flag:

    $ b list -r

You can also use the `-o` flag to filter the list to a specific user, for example:

    $ b list -o george

Would list all of the bugs currently open and assigned to "george".



Editing Bugs
------------------------------------------------------------------------------------------------------------------------
Bugs can be edited outside of `b` by simply opening the ".bug.yaml" file directly from the `.bugs` directory, if you know what the full ID of the bug is.

To make opening bugs for editing easier, you can also use the `edit` command to open the bug using it's prefix in your [configured editor](commands/config.md#editor) for further editing.  For example:

    $ b edit 6
