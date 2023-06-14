Editing Commands
========================================================================================================================
These commands all modify the bug's YAML file in some way - usually just convenience methods for modifying specific attributes of the bug.



Add Command
------------------------------------------------------------------------------------------------------------------------
To file a new bug, all you have to do is run:

    $ b add "This is a new bug"

And you can confirm it's been added by calling:

    $ b list

Which will show you your new bug, along with an ID to refer to it by.  These IDs are actually prefixes of the full bug ID and will get longer as more bugs are added.  See the `id` command for more info about IDs and prefixes.




Edit Command
------------------------------------------------------------------------------------------------------------------------
To edit the details for a bug, use the edit command:

    $ b edit <prefix>

This will open the YAML file for the bug in the editor of your choice (set via the `editor` [[config]] option) allowing you to edit all of the bug's details directly.




Rename Command
------------------------------------------------------------------------------------------------------------------------
To rename a bug, you can call:

    $ b rename <prefix> "New name here"

Alternatively, you could use the `edit` command to open the YAML file directly and edit the title there.




Assign Command
------------------------------------------------------------------------------------------------------------------------
To assign a bug to a user, use the assign command:

    $ b assign <prefix> <owner>

By default, `b` will use the "owner" that you specify to match against users already associated with bugs in the .bugs directory.  If you're assigning a bug to a new user you will get a message that reads something like

    b: error: The provided user - username - did not match any users in the system. Use -f to force the creation of a new user.

This is normal, and is simply trying to ensure that you're aware that you're assigning the bug to a user that hasn't already been used.  Simply re-issue the command and tack on a `-f`.

The "owner" can have a couple of special values too:

me
:   Will assign the bug to you - the username set via the `user` [[config]] option.

nobody
:   Will unassign the bug from any current ownership.




Resolve Command
------------------------------------------------------------------------------------------------------------------------
When you're finished with a bug, simply call

    $ b resolve <prefix>

This will switch the open flag to `False` in the YAML.  You could alternatively use the `edit` command to open the YAML and manually change `open` to `False`.

Use the `reopen` command to reverse this action.




Reopen Command
------------------------------------------------------------------------------------------------------------------------
The opposite of the `resolve` command above - sets the open flag to `True`.

    $ b reopen <prefix>




Comment Command
------------------------------------------------------------------------------------------------------------------------
To add a new comment to the comments section of a bug, which also include the comment author's info and a timestamp, use the `comment` command, as follows:

    $ b comment <prefix> "Comment text"

This will append your comment to the YAML file along with the date and your username from the [[config]] file.

Comments are especially helpful for documenting the progress and status of the investigative or corrective action steps of a bug.
