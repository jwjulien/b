# ======================================================================================================================
#        File:  command.py
#     Project:  B Bug Tracker
# Description:  Simple bug tracker
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022-2023 Jared Julien <jaredjulien@exsystems.net>
# ---------------------------------------------------------------------------------------------------------------------
"""Standalone command line interface for b.

Because this is standalone and does not involve Mercurial, the bits regarding specifying a revision have been stripped.
"""

# ======================================================================================================================
# Import Statements
# ----------------------------------------------------------------------------------------------------------------------
import os
from argparse import ArgumentParser
import logging
from importlib import metadata
import getpass

from rich import print
from rich_argparse import RichHelpFormatter
from rich.logging import RichHandler

from b.bugs import Tracker
from b.settings import Settings
from b import exceptions





# ======================================================================================================================
# Helper Functions
# ----------------------------------------------------------------------------------------------------------------------
def _add_arg_template(parser):
    """Add an argument to specify the template to use when creating a new details file along with the command."""
    parser.add_argument(
        '-t',
        '--template',
        help='specify template for new detail file (default: bug) - use `templates` command to list templates'
    )


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
    _add_arg_template(parser)


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




# ======================================================================================================================
# Command Line Processing
# ----------------------------------------------------------------------------------------------------------------------
def run():
    description = metadata.metadata('b')['Summary']
    version = metadata.version('b')
    parser = ArgumentParser(description=description, formatter_class=RichHelpFormatter)

    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help='increase verbosity of output'
    )

    commands = parser.add_subparsers(title='command', dest='command')

    parser_init = commands.add_parser('init',
                                      help='initialize a bugs directory for new bugs',
                                      formatter_class=RichHelpFormatter)
    parser_init.add_argument(
        '-f',
        '--force',
        action='store_true',
        default=False,
        help='force the creation of a bugs directory in this location, even if one exists above this level'
    )

    parser_add = commands.add_parser('add',
                                     help='adds a new open bug to the database',
                                     formatter_class=RichHelpFormatter)
    _add_arg_text(parser_add, 'title text for the new bug')
    _add_arg_edit(parser_add)

    parser_rename = commands.add_parser('rename',
                                        help='rename the bug denoted by PREFIX to TEXT',
                                        formatter_class=RichHelpFormatter)
    _add_arg_prefix(parser_rename)
    _add_arg_text(parser_rename, 'new title text for the bug')
    _add_arg_edit(parser_rename)

    commands.add_parser('users', help='display a list of all users and the number of open bugs assigned to each')

    parser_assign = commands.add_parser('assign',
                                        help='assign bug denoted by PREFIX to username',
                                        formatter_class=RichHelpFormatter)
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

    parser_details = commands.add_parser('details',
                                         help='print the extended details of the specified bug',
                                         formatter_class=RichHelpFormatter)
    _add_arg_prefix(parser_details)
    _add_arg_edit(parser_details)

    parser_edit = commands.add_parser('edit',
                                      help='launch the system editor to provide additional details',
                                      formatter_class=RichHelpFormatter)
    _add_arg_prefix(parser_edit)
    _add_arg_template(parser_edit)

    parser_comment = commands.add_parser('comment',
                                         help='append the provided comment to the details of the bug',
                                         formatter_class=RichHelpFormatter)
    _add_arg_prefix(parser_comment)
    _add_arg_text(parser_comment, 'comment text to append')
    _add_arg_edit(parser_comment)

    parser_resolve = commands.add_parser('resolve',
                                         help='mark the specified bug as resolved',
                                         formatter_class=RichHelpFormatter)
    _add_arg_prefix(parser_resolve)
    _add_arg_edit(parser_resolve)

    parser_reopen = commands.add_parser('reopen',
                                        help='mark the specified bug as open',
                                        formatter_class=RichHelpFormatter)
    _add_arg_prefix(parser_reopen)
    _add_arg_edit(parser_reopen)

    parser_list = commands.add_parser('list',
                                      help='list all bugs according to the specified filters',
                                      formatter_class=RichHelpFormatter)
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

    parser_id = commands.add_parser('id',
                                    help='given a prefix return the full ID of a bug',
                                    formatter_class=RichHelpFormatter)
    _add_arg_prefix(parser_id)
    _add_arg_edit(parser_id)

    parser_templates = commands.add_parser('templates',
                                           help='list templates available when creating new bug reports',
                                           formatter_class=RichHelpFormatter)
    parser_templates.add_argument(
        '-d',
        '--defaults',
        action='store_true',
        default=False,
        help='list only the default templates - no custom templates from the .bugs directory of the project'
    )
    parser_templates.add_argument(
        '-c',
        '--custom',
        metavar='TEMPLATE',
        help='copy the specified template to the project directory for customization'
    )
    parser_templates.add_argument(
        '-e',
        '--edit',
        metavar='TEMPLATE',
        help='open the custom template for editing'
    )

    config_parser = commands.add_parser('config',
                                        help='adjust configurations - default lists all',
                                        formatter_class=RichHelpFormatter)
    config_parser.add_argument(
        'key',
        nargs='?',
        help='the name of the setting'
    )
    config_parser.add_argument(
        'value',
        nargs='?',
        help='the value of the setting to set'
    )
    config_parser.add_argument(
        '-u',
        '--unset',
        action='store_true',
        default=False,
        help='restore variable to default value'
    )

    commands.add_parser('migrate',
                        help='migrate bugs directory to the latest version',
                        formatter_class=RichHelpFormatter)

    commands.add_parser('version',
                        help='output the version number of b and exit',
                        formatter_class=RichHelpFormatter)

    # Parser arguments from the command line - with a special case for no command which defaults to "list".
    args, extras = parser.parse_known_args()
    if args.command is None:
        args.comment = 'list'
        args = parser_list.parse_args(extras, namespace=args)

    # If the text argument is present join the possible multiple values into a single string.
    if 'text' in args:
        args.text = ' '.join(args.text).strip()

    # Setup logging output.
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(2, args.verbose)]
    logging.basicConfig(level=level, format='%(message)s', datefmt="[%X]", handlers=[RichHandler()])

    defaults = {
        'general.editor': 'notepad' if os.name == 'nt' else 'nano',
        'general.dir': '.bugs',
        'general.user': getpass.getuser()
    }
    with Settings(defaults) as settings:
        # Load the bug dictionary from the bugs file.
        tracker = Tracker(settings.get('dir'), settings.get('user'), settings.get('editor'))

        logging.info('Bugs directory: %s', tracker.bugsdir)

        logging.debug('Current settings:')
        logging.debug('- dir = "%s"', settings.get('dir'))
        logging.debug('- user = "%s"', settings.get('user'))
        logging.debug('- editor = "%s"', settings.get('editor'))

        logging.debug('Issued command: "%s"', args.command)

        try:
            # Handle the specified command.
            if args.command == 'add':
                tracker.add(args.text, args.template)

            elif args.command == 'init':
                tracker.initialize(args.force)

            elif args.command == 'assign':
                tracker.assign(args.prefix, args.username, args.force)

            elif args.command == 'comment':
                tracker.comment(args.prefix, args.text, args.template)

            elif args.command == 'details':
                tracker.details(args.prefix)

            elif args.command == 'edit':
                tracker.edit(args.prefix, args.template)

            elif args.command == 'id':
                tracker.id(args.prefix)

            elif args.command is None or args.command == 'list':
                if tracker.bugs_filename is None:
                    print('Bug reporting not initialized')
                else:
                    tracker.list(not args.resolved, args.owner, args.grep, args.alpha, args.chrono)

            elif args.command == 'rename':
                tracker.rename(args.prefix, args.text)

            elif args.command == 'resolve':
                tracker.resolve(args.prefix)

            elif args.command == 'reopen':
                tracker.reopen(args.prefix)

            elif args.command == 'users':
                tracker.users()

            elif args.command == 'templates':
                if args.custom:
                    tracker.customize_template(args.custom)
                elif args.edit:
                    tracker.edit_template(args.edit)
                else:
                    print(f"Available {'default ' if args.defaults else ''}bug templates:")
                    templates = tracker.list_templates(only_defaults=args.defaults)
                    for name in sorted(templates.keys()):
                        print(f'- {name} ({templates[name]})')

            elif args.command == 'config':
                if args.unset:
                    if not args.key:
                        raise exceptions.Error('Provide a key to be unset')
                    settings.unset(args.key)
                elif args.value is not None:
                    # Set the value of the key
                    settings.set(args.key, args.value)
                    print(f'"{args.key}" set to "{args.value}"')
                elif args.key is not None:
                    # Fetch the value of the key.
                    print(args.key, '=', settings.get(args.key))
                else:
                    # List the current settings.
                    if settings.exists:
                        print(f'Config file is located at {settings.file}')
                    else:
                        print('All settings are currently defaults')
                    for key, value in settings.list():
                        print(f'{key}={value}')

            elif args.command == 'migrate':
                tracker.migrate()

            elif args.command == 'version':
                print(f'b version {version}')

            else:
                raise exceptions.UnknownCommand(args.command)

        except exceptions.Error as error:
            parser.error(str(error))
            return 1

        else:
            if 'edit' in args and args.edit:
                prefix = args.prefix if 'prefix' in args else tracker.last_added_id
                tracker.edit(prefix, args.template)

    return 0




# End of File
