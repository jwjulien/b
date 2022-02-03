# ======================================================================================================================
#        File:  command.py
#     Project:  B Bug Tracker
# Description:  Distributed Bug Tracker Extention for Mercurial
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022 Jared Julien, Nexteer Automotive
# ---------------------------------------------------------------------------------------------------------------------
"""Standalone command line interface for b.

Because this is standalone and does not involve Mercurial, the bits regarding specifying a revision have been stripped.
"""

# ======================================================================================================================
# Import Statements
# ----------------------------------------------------------------------------------------------------------------------
import os
from argparse import ArgumentParser
from configparser import ConfigParser
import importlib_metadata

from bugs_dict import BugsDict
import exceptions





# ======================================================================================================================
# Helper Functions
# ----------------------------------------------------------------------------------------------------------------------
def _add_arg_edit(parser):
    """The edit flag is common across several subparsers.  This helper sets the same attributes for each."""
    parser.add_argument(
        '-e',
        '--edit',
        action='store_true',
        default=False,
        help='launch details editor for the bug'
    )


# ----------------------------------------------------------------------------------------------------------------------
def _add_arg_prefix(parser):
    """Add the common prefix argument to the provided parser."""
    parser.add_argument(
        'prefix',
        help='prefix of the bug'
    )


# ----------------------------------------------------------------------------------------------------------------------
def _add_arg_text(parser, help):
    """Add the common TEXT input argument to the provided parser."""
    parser.add_argument(
        'text',
        nargs='+',
        help=help
    )


# ----------------------------------------------------------------------------------------------------------------------
def _get_user():
    """Attempt to fetch and return the user's name from the mercurial.ini file.

    This has ties to b originally being a part of Mercurial and the file is most likely going to be present on systems
    where b is being used, even as this version not associated with Mercurial.  It may be a better option for b to make
    use of a separate config file, but that change can happen later.

    If the mercurial.ini isn't found or if the user's name is not set then a blank string is returned instead.
    """
    path = os.path.expanduser(os.path.join('~', 'mercurial.ini'))
    if os.path.exists(path):
        parser = ConfigParser()
        parser.read(path)
        return parser.get('ui', 'username', fallback='')
    return ''




# ======================================================================================================================
# Command Line Processing
# ----------------------------------------------------------------------------------------------------------------------
def run():
    parser = ArgumentParser(description="A simplistic, distributed bug tracing utility.")
    parser.add_argument(
        '-d',
        '--dir',
        default='.bugs',
        help='directory containing the bugs (default: .bugs)'
    )
    parser.add_argument(
        '-u',
        '--user',
        default=_get_user(),
        help='your username - attempts to extract from mercurial.ini if not provided'
    )
    parser.add_argument(
        '-E',
        '--editor',
        default='notepad' if os.name == 'nt' else 'nano',
        help='specify the editor that you would like to use when editing bug details'
    )
    commands = parser.add_subparsers(title='command', dest='command')

    parser_add = commands.add_parser('add', help='adds a new open bug to the database')
    _add_arg_text(parser_add, 'title text for the new bug')
    _add_arg_edit(parser_add)

    parser_rename = commands.add_parser('rename', help='rename the bug denoted by PREFIX to TEXT')
    _add_arg_prefix(parser_rename)
    _add_arg_text(parser_rename, 'new title text for the bug')
    _add_arg_edit(parser_rename)

    commands.add_parser('users', help='display a list of all users and the number of open bugs assigned to each')

    parser_assign = commands.add_parser('assign', help='assign bug denoted by PREFIX to username')
    _add_arg_prefix(parser_assign)
    parser_assign.add_argument(
        'username',
        help='username of user to be assigned - can be a prefix of an existing user or "nobody" to unassign'
    )
    parser_assign.add_argument(
        '-f',
        '--force',
        action='store_true',
        default=False,
        help='do not attempt to map USERNAME as a prefix, instead use the provided username verbatim'
    )
    _add_arg_edit(parser_assign)

    parser_details = commands.add_parser('details', help='print the extended details of the specified bug')
    _add_arg_prefix(parser_details)
    _add_arg_edit(parser_details)

    parser_edit = commands.add_parser('edit', help='launch the system editor to provide additional details')
    _add_arg_prefix(parser_edit)

    parser_comment = commands.add_parser('comment', help='append the provided comment to the details of the bug')
    _add_arg_prefix(parser_comment)
    _add_arg_text(parser_comment, 'comment text to append')
    _add_arg_edit(parser_comment)

    parser_resolve = commands.add_parser('resolve', help='mark the specified bug as resolved')
    _add_arg_prefix(parser_resolve)
    _add_arg_edit(parser_resolve)

    parser_reopen = commands.add_parser('reopen', help='mark the specified bug as open')
    _add_arg_prefix(parser_reopen)
    _add_arg_edit(parser_reopen)

    parser_list = commands.add_parser('list', help='list all bugs according to the specified filters')
    parser_list.add_argument(
        '-r',
        '--resolved',
        action='store_true',
        default=False,
        help='include resolved bugs'
    )
    parser_list.add_argument(
        '-o',
        '--owner',
        default='*',
        help='"*" lists all, "nobody" lists unassigned, otherwise text to matched against username'
    )
    parser_list.add_argument(
        '-g',
        '--grep',
        default='',
        help='filter by the search string appearing in the title'
    )
    sort_group = parser_list.add_mutually_exclusive_group()
    sort_group.add_argument(
        '-a',
        '--alpha',
        action='store_true',
        default=False,
        help='list bugs alphabetically'
    )
    sort_group.add_argument(
        '-c',
        '--chrono',
        action='store_true',
        default=False,
        help='list bugs chronologically'
    )

    parser_id = commands.add_parser('id', help='given a prefix return the full ID of a bug')
    _add_arg_prefix(parser_id)
    _add_arg_edit(parser_id)

    commands.add_parser('version', help='output the version number of b and exit')

    # Parser arguments from the command line - with a special case for no command which defaults to "list".
    args, extras = parser.parse_known_args()
    if args.command is None:
        args.comment = 'list'
        args = parser_list.parse_args(extras, namespace=args)

    # If the text argument is present join the possible multiple values into a single string.
    if 'text' in args:
        args.text = ' '.join(args.text).strip()

    # Load the bug dictionary from the bugs file.
    bugs = BugsDict(args.dir, args.user)

    try:
        # Handle the specified command.
        if args.command == 'add':
            print(bugs.add(args.text))

        elif args.command == 'assign':
            print(bugs.assign(args.prefix, args.username, args.force))

        elif args.command == 'comment':
            bugs.comment(args.prefix, args.text)

        elif args.command == 'details':
            print(bugs.details(args.prefix))

        elif args.command == 'edit':
            bugs.edit(args.prefix, args.editor)

        elif args.command == 'id':
            print(bugs.id(args.prefix))

        elif args.command is None or args.command == 'list':
            print(bugs.list(not args.resolved, args.owner, args.grep, args.alpha, args.chrono))

        elif args.command == 'rename':
            bugs.rename(args.prefix, args.text)

        elif args.command == 'resolve':
            bugs.resolve(args.prefix)

        elif args.command == 'reopen':
            bugs.reopen(args.prefix)

        elif args.command == 'users':
            print(bugs.users())

        elif args.command == 'version':
            print(f'b version {importlib_metadata.version("b")}')

        else:
            raise exceptions.UnknownCommand(args.command)

    except exceptions.Error as err:
        print(err.msg)
        return 1

    else:
        bugs.write()

        if 'edit' in args and args.edit:
            prefix = args.prefix if 'prefix' in args else bugs.last_added_id
            bugs.edit(prefix, args.editor)

    return 0




# End of File
