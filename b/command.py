# ======================================================================================================================
#        File:  command.py
#     Project:  B Bug Tracker
# Description:  Simple bug tracker
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022-2023 Jared Julien <jaredjulien@exsystems.net>
# ---------------------------------------------------------------------------------------------------------------------
"""Command line interface for b."""

# ======================================================================================================================
# Import Statements
# ----------------------------------------------------------------------------------------------------------------------
import os
import logging
from importlib import metadata

import click
from rich import print
from rich.logging import RichHandler

from b.bugs import Tracker
from b.settings import Settings




# ======================================================================================================================
# CLI Application Base
# ----------------------------------------------------------------------------------------------------------------------
@click.group(invoke_without_command=True)
@click.option('-v', 'verbose', count=True, help='increase verbosity of output')
@click.pass_context
def cli(ctx, verbose):
    """A simple, distributed bug tracker."""
    ctx.ensure_object(dict)

    # Setup logging output.
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(2, verbose)]
    logging.basicConfig(level=level, format='%(message)s', datefmt="[%X]", handlers=[RichHandler()])

    ctx.obj['settings'] = Settings()
    ctx.obj['tracker'] = Tracker(
        ctx.obj['settings'].get('dir'),
        ctx.obj['settings'].get('user'),
        ctx.obj['settings'].get('editor')
    )

    # Run list command with default settings if no command was issued.
    if ctx.invoked_subcommand is None:
        ctx.obj['tracker'].list()




# ======================================================================================================================
# Commands
# ----------------------------------------------------------------------------------------------------------------------
@cli.command()
@click.option('-f', '--force', is_flag=True, help='force creation of .bugs directory at this location')
@click.pass_context
def init(ctx, force: bool):
    """Initialize a bugs directory for new bugs."""
    ctx.obj['tracker'].initialize(force)



# ----------------------------------------------------------------------------------------------------------------------
@cli.command()
@click.argument('title')
@click.option('-s', '--self', is_flag=True, help='assign me as owner of this new bug, default is unowned')
@click.option('-t', '--template', default='bug', help='specify the template to use for this bug')
@click.option('-e', '--edit', is_flag=True, help='open this new bug for editing after creating')
@click.pass_context
def add(ctx, title: str, self: bool, template: str, edit: bool):
    """Add a new, open bug to the tracker.

    TITLE specifies the short summary text to to serve as a title for the bug.

    The `template` can be specified using the '-t' or '--template' option.  The default template is "bug".  A complete
    list of available templates can be found using the "template list" command.
    """
    prefix = ctx.obj['tracker'].add(title, template, self)
    if edit:
        ctx.obj['tracker'].edit(prefix)


# ----------------------------------------------------------------------------------------------------------------------
@cli.command()
@click.argument('prefix')
@click.argument('title')
@click.option('-e', '--edit', is_flag=True, help='open this bug for editing after changing the title')
@click.pass_context
def rename(ctx, prefix: str, title: str, edit: bool):
    """Change the title of the bug denoted by PREFIX to the new TITLE."""
    ctx.obj['tracker'].rename(prefix, title)
    if edit:
        ctx.obj['tracker'].edit(prefix)



# ----------------------------------------------------------------------------------------------------------------------
@cli.command()
@click.option('-d', '--detailed', is_flag=True, help='list individual bugs for each owner')
@click.option('-o', '--open', 'scope', flag_value='open', default=True, help='show only open bugs')
@click.option('-r', '--resolved', 'scope', flag_value='resolved', help='list only resolved bugs')
@click.option('-a', '--all', 'scope', flag_value='all', help='')
@click.pass_context
def users(ctx, detailed: bool, scope: str):
    """Display a list of all users and the number of open bugs assigned to each.

    By default, only the count of bugs for each owner are shown.  Use the '-d' flag to list individual bugs for each
    user if more information is desired.

    By default, only open bugs are displayed for each user.  To list resolved bugs instead, use the '-r' option or to
    list all bugs (both open and resolved) use the '-a' switch.
    """
    ctx.obj['tracker'].users(scope, detailed)


# ----------------------------------------------------------------------------------------------------------------------
@cli.command()
@click.argument('prefix')
@click.argument('username')
@click.option('-f', '--force', is_flag=True, help='force the user of USERNAME verbatim')
@click.pass_context
def assign(ctx, prefix: str, username: str, force: bool):
    """Assign bug denoted by PREFIX to USERNAME.

    USERNAME can be specified as "nobody" to remove ownership of the bug.

    The USERNAME can be a prefix of any username that is enough to uniquely identify an existing user.  For example,
    providing a USERNAME of "mi" would be enough to identify a "michael" from a project where "michael" and "mark" are
    existing users.  If you would like to assign a new user explicitly without this prefix-matching functionality use
    the '-f' flag to force the assignment instead.
    """
    ctx.obj['tracker'].assign(prefix, username, force)


# ----------------------------------------------------------------------------------------------------------------------
@cli.command()
@click.argument('prefix')
@click.pass_context
def details(ctx, prefix: str):
    """Print the extended details of the bug specified by PREFIX."""
    ctx.obj['tracker'].details(prefix)


# ----------------------------------------------------------------------------------------------------------------------
@cli.command()
@click.argument('prefix')
@click.pass_context
def edit(ctx, prefix: str):
    """Launch the system editor to provide additional details."""
    ctx.obj['tracker'].edit(prefix)


# ----------------------------------------------------------------------------------------------------------------------
@cli.command()
@click.argument('prefix')
@click.argument('comment')
@click.option('-e', '--edit', is_flag=True, help='open this bug for editing after adding comment')
@click.pass_context
def comment(ctx, prefix: str, comment: str, edit: bool):
    """Append the provided COMMENT to the details of the bug identified by PREFIX."""
    ctx.obj['tracker'].comment(prefix, comment)
    if edit:
        ctx.obj['tracker'].edit(prefix)


# ----------------------------------------------------------------------------------------------------------------------
@cli.command()
@click.argument('prefix')
@click.pass_context
def resolve(ctx, prefix: str):
    """Mark the bug identified by PREFIX as resolved."""
    ctx.obj['tracker'].resolve(prefix)


# ----------------------------------------------------------------------------------------------------------------------
@cli.command()
@click.argument('prefix')
@click.pass_context
def reopen(ctx, prefix: str):
    """Mark the bug identified by PREFIX as open."""
    ctx.obj['tracker'].reopen(prefix)


# ----------------------------------------------------------------------------------------------------------------------
@cli.command()
@click.option('-O', '--open', 'scope', flag_value='open', default=True, help='list only open bugs')
@click.option('-r', '--resolved', 'scope', flag_value='resolved', help='list only resolved bugs')
@click.option('-a', '--all', 'scope', flag_value='all', help='list all bugs - open and resolved')
@click.option('-o', '--owner', default='*', help='list bugs assigned to OWNER')
@click.option('-g', '--grep', default='', help='filter results against GREP pattern')
@click.option('-d', '--descending', is_flag=True, help='sort results in descending order')
@click.option('-t', '--title', 'sort', flag_value='title', help='sort bug alphabetically by title')
@click.option('-e', '--entered', 'sort', flag_value='entered', help='sort bugs chronologically by entered date')
@click.pass_context
def list(ctx, scope: str, owner: str, grep: str, descending: bool, sort: str):
    """List all bugs according to the specified filters."""
    ctx.obj['tracker'].list(scope, owner, grep, sort, descending)


# ----------------------------------------------------------------------------------------------------------------------
@cli.command()
@click.argument('prefix')
@click.pass_context
def id(ctx, prefix: str):
    """Print the full ID of the buf identified by PREFIX."""
    ctx.obj['tracker'].id(prefix)


# ----------------------------------------------------------------------------------------------------------------------
@cli.command()
@click.pass_context
def verify(ctx):
    """Verify that all bug YAML files are valid and report any discrepancies."""
    ctx.obj['tracker'].verify()


# ----------------------------------------------------------------------------------------------------------------------
@cli.group()
@click.option('-c', '--custom', )
def templates():
    """Configure the bug templates available to this project."""


# ----------------------------------------------------------------------------------------------------------------------
@templates.command()
@click.option('-d', '--defaults', is_flag=True, help='list only the available non-customized templates')
@click.pass_context
def list(ctx, defaults: bool):
    """List the templates that are available to the `add` command."""
    print(f"Available {'default ' if defaults else ''}bug templates:")
    templates = ctx.obj['tracker'].list_templates(only_defaults=defaults)
    for name in sorted(templates.keys()):
        base = os.path.relpath(os.path.dirname(templates[name]), os.path.dirname(ctx.obj['tracker'].bugsdir))
        filename = os.path.basename(templates[name])
        sep = os.path.sep.replace('\\', '\\\\')
        print(f'- [green]{name}[/] ([italic]{base}{sep}[yellow]{filename}[/])')


# ----------------------------------------------------------------------------------------------------------------------
@templates.command()
@click.argument('template')
@click.pass_context
def customize(ctx, template: str):
    """Customize the TEMPLATE for this project."""
    ctx.obj['tracker'].customize_template(template)


# ----------------------------------------------------------------------------------------------------------------------
@templates.command(name='edit')
@click.argument('template')
@click.pass_context
def edit_template(ctx, template: str):
    ctx.obj['tracker'].edit_template(template)


# ----------------------------------------------------------------------------------------------------------------------
@cli.group()
def config():
    """Change configuration settings for b."""


# ----------------------------------------------------------------------------------------------------------------------
@config.command()
@click.argument('key')
@click.pass_context
def unset(ctx, key):
    """Remove the saved setting identified by KEY.

    This restores the setting to it's default value.

    To list the current settings, issue the "config list" command.
    """
    ctx.obj['settings'].unset(key)
    ctx.obj['settings'].store()


# ----------------------------------------------------------------------------------------------------------------------
@config.command()
@click.pass_context
def set(ctx, key: str, value: str):
    """Set the setting identified by KEY to the provided VALUE."""
    ctx.obj['settings'].set(key, value)
    print(f'"{key}" set to "{value}"')
    ctx.obj['settings'].store()


# ----------------------------------------------------------------------------------------------------------------------
@config.command()
@click.argument('key')
@click.pass_context
def get(ctx, key: str):
    """Get the current value for the setting identified by KEY."""
    print(key, '=', ctx.obj['settings'].get(key))


# ----------------------------------------------------------------------------------------------------------------------
@config.command()
@click.pass_context
def list(ctx):
    """List all of the currently configured settings."""
    if ctx.obj['settings'].exists:
        print(f"Config file is located at {ctx.obj['settings'].file}")
    else:
        print('All settings are currently defaults')

    for key, value in ctx.obj['settings'].list():
        print(f'{key}={value}')
        # TODO: Indicate which settings are defaults.


# ----------------------------------------------------------------------------------------------------------------------
@cli.command()
@click.pass_context
def migrate(ctx):
    """Migrate bugs directory to the latest version."""
    ctx.obj['tracker'].migrate()


# ----------------------------------------------------------------------------------------------------------------------
@cli.command()
def version():
    """Output the version information and exit."""
    version = metadata.version('b')
    print(f'b version {version}')




# End of File
