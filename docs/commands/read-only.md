Read-Only Commands
========================================================================================================================
The following commands do not modify any information about bugs but rather aggregate and present information about them.




ID Command
------------------------------------------------------------------------------------------------------------------------
Bugs are generally referenced iun `b` using their *prefix* rather than the full ID, for convenience.  It is important to note that these prefixes can and will change over time as new bugs are added.  The prefix is simply the minimum number of leading characters needed to uniquely identify the bug within all bugs listed in the .bugs directory.

If you need a permanent reference to a bug, you can pass a prefix to the `id` command.

    $ b id <prefix>

This will return the full ID of the bug which will never change.

You'll likely only ever need the first eight or so characters - a database of 20,000+ bugs only used the first four or five in most cases.




List Command
------------------------------------------------------------------------------------------------------------------------
To list all of the open bugs, issue:

    $ b list

Or, as list is the default command, simply:

    $ b

The list command output can be tweaked using a number of flags in various combinations:

* `-r`: list resolved bugs, instead of open bugs
* `-a`: list all bugs, open and resolved
* `-o`: takes a username (or a username prefix) and lists bugs owned by the specified user
* `-g`: list bugs which contain the specified text in their title
* `-t`: sort issues by title in alphabetical order
* `-e`: sort issues chronologically by entered date
* `-d`: list im descending order (best used with `-t` or `-e` to reverse the order)

These flags can be used together for fairly granular browsing of your bugs database.




Details Command
------------------------------------------------------------------------------------------------------------------------
To get a report listing all of the details from the YAML of a single bug, use the `details` command:

    $ b details <prefix>


This provides some basic metadata like date filed and owner, along with the contents of the details file, if it exists.  Any sections (denoted by text in square brackets) which are empty are not displayed by the details command to simplify the output.




Users Command
------------------------------------------------------------------------------------------------------------------------
To generate a report that shows the number of open bugs assigned to each user run:

    $ b users

To see the bugs associated with each used use the `-d` switch:

    $ b users -d

`b` will then produce a tree showing each user and the bugs then have been assigned to under each.

By default, the `users` command shows *open* bugs assigned to each user.  To see *resolved* bugs instead, use the `-r` switch.  Or, to see *all* bugs, use the `-a` switch instead.
