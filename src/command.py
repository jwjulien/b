# ======================================================================================================================
#        File:  command.py
#     Project:  B Bug Tracker
# Description:  Distributed Bug Tracker Extention for Mercurial
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022 Jared Julien, Nexteer Automotive
# ---------------------------------------------------------------------------------------------------------------------
"""Extensions that integrate b into Mercurial.
"""

# ======================================================================================================================
# Import Statements
# ----------------------------------------------------------------------------------------------------------------------
from argparse import ArgumentParser
import os
import sys
import tempfile
import traceback
from mercurial.error import Abort
from mercurial import commands, registrar

from b import __version__
import exceptions
import helpers
import decorators
from bugs_dict import BugsDict
from interface import CLI




# ======================================================================================================================
# Comand Line Processing
# ----------------------------------------------------------------------------------------------------------------------
def run():
    description = """Distributed Bug Tracker For Mercurial

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
    parser = ArgumentParser(description=description)
    parser.add_argument(
        '-f',
        '--force',
        action='store_true',
        default=False,
        help='force this exact username'
    )
    parser.add_argument(
        '-e',
        '--edit',
        action='store_true',
        default=False,
        help='launch details editor after running command'
    )
    parser.add_argument(
        '-r',
        '--resolved',
    )
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


# # ----------------------------------------------------------------------------------------------------------------------
# def execute_command(ui, repo, cmd=b'list', *args, **opts):
#     """
#     """
#     try:
#         try:
#             _CLI(ui, repo).invoke(cmd, *args, **opts)
#         except Exception:
#             if 'HG_B_LOG_TRACEBACKS' in os.environ:
#                 traceback.print_exc(file=sys.stderr)
#                 sys.stderr.write("\n")
#             raise
#     except exceptions.Error as e:
#         ui.warn(b'%s\n' % e.msg.encode('utf-8'))
#         return 1






# End of File
