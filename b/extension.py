# ======================================================================================================================
#        File:  extension.py
#     Project:  B Bug Tracker
# Description:  Distributed Bug Tracker Extension for Mercurial
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022-2023 Jared Julien <jaredjulien@exsystems.net>
# ---------------------------------------------------------------------------------------------------------------------
"""Extensions that integrate b into Mercurial."""

# ======================================================================================================================
# Import Statements
# ----------------------------------------------------------------------------------------------------------------------
import os
import sys
import traceback
from importlib.metadata import distribution
from mercurial import commands, registrar

from b import exceptions
from b import helpers
from b.interface import CLI




# ======================================================================================================================
# Mercurial-related Globals
# ----------------------------------------------------------------------------------------------------------------------
cmdtable = {}
command = registrar.command(cmdtable)
testedwith = '4.7'  # And others circa 2010, before this variable existed
buglink = 'http://hg.mwdiamond.com/b'




# ======================================================================================================================
# Comand Line Processing
# ----------------------------------------------------------------------------------------------------------------------
@command(b"b|bug|bugs", [
    (b'f', b'force', False, b'Force this exact username'),
    (b'e', b'edit', False, b'Launch details editor after running command'),
    (b'r', b'resolved', False, b'List resolved bugs'),
    (b'o', b'owner', b'*', b'Specify an owner to list by'),
    (b'g', b'grep', b'', b'Filter titles by STRING'),
    (b'a', b'alpha', False, b'Sort list alphabetically'),
    (b'c', b'chrono', False, b'Sort list chronologically'),
    (b'T', b'truncate', False, b'Truncate list output to fit window'),
    (b'', b'rev', b'',
    b'Run a read-only command against a different revision')
], b"cmd [args]")


# ----------------------------------------------------------------------------------------------------------------------
def execute_command(ui, repo, cmd=b'list', *args, **opts):
    """Distributed Bug Tracker For Mercurial

    List of Commands::

    add text [-e]
        Adds a new open bug to the database, if user is set in the config files,
        assigns it to user

        -e here and elsewhere launches the details editor for the issue upon
        successful execution of the command

    rename prefix text [-e]
        Renames The bug denoted by prefix to text.   You can use sed-style
        substitution strings if so desired.

    users [--rev rev]
        Displays a list of all users, and the number of open bugs assigned to
        each of them

    assign prefix username [-f] [-e]
        Assigns bug denoted by prefix to username.  Username can be a lowercase
        prefix of another username and it will be mapped to that username. To
        avoid this functionality and assign the bug to the exact username
        specified, or if the user does not already exist in the bugs system, use
        the -f flag to force the name.

        Use 'me' to assign the bug to the current user,
        and 'Nobody' to remove its assignment.

    details [--rev rev] prefix [-e]
        Prints the extended details of the specified bug

    edit prefix
        Launches your specified editor to provide additional details

    comment prefix comment [-e]
        Appends comment to the details of the bug, along with the date
        and, if specified, your username without needing to launch an editor

    resolve prefix [-e]
        Marks the specified bug as resolved

    reopen prefix [-e]
        Marks the specified bug as open

    list [--rev rev] [-r] [-o owner] [-g search] [-a|-c]
        Lists all bugs, with the following filters:

            -r list resolved bugs.

            -o list bugs assigned to owner.  '*' will list all bugs, 'me' will
               list all bugs assigned to the current user, and 'Nobody' will
               list all unassigned bugs.

            -g filter by the search string appearing in the title

            -a list bugs alphabetically

            -c list bugs chronologically

    id [--rev rev] prefix [-e]
        Takes a prefix and returns the full id of that bug

    version
        Outputs the version number of b being used in this repository
    """
    try:
        try:
            # TODO: I think the args could be passed in to the standard command line processor reducing duplicated
            # functionality here.  Would need to generate an abstraction for ui though.
            CLI(ui, repo).invoke(cmd, *args, **opts)
        except Exception:
            if 'HG_B_LOG_TRACEBACKS' in os.environ:
                traceback.print_exc(file=sys.stderr)
                sys.stderr.write("\n")
            raise
    except exceptions.Error as e:
        ui.warn(b'%s\n' % e.msg.encode('utf-8'))
        return 1




# ======================================================================================================================
# Programmatic access to b
# ----------------------------------------------------------------------------------------------------------------------
def version(given_version=None):
    """Returns a numerical representation of the version number, or takes a
    version string.

    Can be used for comparison:
        b.version() > b.version("0.7.0")

    Note: Before version 0.6.2 this function did not exist. If:
        callable(getattr(b, "version", None))
    returns false, that indicates a version before 0.6.2"""
    if given_version is None:
        given_version = distribution("b").version
    a, b, c = (int(ver) for ver in given_version.split('.') if ver.isdigit())
    return a, b, c


# ----------------------------------------------------------------------------------------------------------------------
def status(ui, repo, revision='tip'):
    """Indicates the state of a revision relative to the bugs database.  In
    essence, this function is a wrapper for `hg stat --change x` which strips
    out changes to the bugs directory.

    A revision either:
    * Does not touch the bugs directory:
      This generally indicates a feature change or other improvement, in any
      case, b cannot draw any conclusions about the revision.
      Returns None.
    * Only touches the bugs directory:
      This would indicate a new bug report, comment, reassignment, or other
      internal b housekeeping.  No external files were touched, no progress is
      being made in the rest of repository.
      Returns an empty list.
    * Touches the bugs directory, and other areas of the repository:
      This is assumed to indicate a bug fix, or progress is being made on a bug.
      Committing unrelated changes to the repository and the bugs database in
      the same revision should be discouraged.
      Returns a list of files outside the bugs directory in the given changeset.

    You may pass a list of Mercurial patterns (see `hg help patterns`) relative
    to the repository root to exclude from the returned list.
    """
    bugsdir = helpers.bugs_dir(ui)
    ui.pushbuffer()
    commands.status(ui, repo, change=revision, no_status=True, print0=True)
    files = ui.popbuffer().split('\0')
    bug_change = False
    ret = []
    for f in files:
        if f.strip():
            if f.startswith(bugsdir):
                bug_change = True
            else:
                ret.append(f)
    ui.write(ret if bug_change else None)
    ui.write('\n')




# End of File
