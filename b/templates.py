# ======================================================================================================================
#        File:  templates.py
#     Project:  B Bug Tracker
# Description:  Simple bug tracker
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022-2023 Jared Julien <jaredjulien@exsystems.net>
# ---------------------------------------------------------------------------------------------------------------------
"""Subcommands for modifying custom templates within projects."""

# ======================================================================================================================
# Import Statements
# ----------------------------------------------------------------------------------------------------------------------
import logging
import os

import click
from rich import print




# ======================================================================================================================
# Template Subcommands
# ----------------------------------------------------------------------------------------------------------------------
@click.group()
def templates():
    """Configure the bug templates available to this project."""


# ----------------------------------------------------------------------------------------------------------------------
@templates.command()
@click.option('-d', '--defaults', is_flag=True, help='list only the available non-customized templates')
@click.pass_context
def list(ctx: click.Context, defaults: bool):
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
def customize(ctx: click.Context, template: str):
    """Customize the TEMPLATE for this project."""
    ctx.obj['tracker'].customize_template(template)
    # TODO: Consider a second, "global" option for custom templates that allow reuse across all user's projects.


# ----------------------------------------------------------------------------------------------------------------------
@templates.command()
@click.argument('template')
@click.pass_context
def edit(ctx: click.Context, template: str):
    """Open custom TEMPLATE for editing."""
    try:
        ctx.obj['tracker'].edit_template(template)
    except FileNotFoundError:
        logging.error('Custom template "%s" does not exit.', template)
        print('To create a new custom template, use the "templates customize" command')




# End of File
