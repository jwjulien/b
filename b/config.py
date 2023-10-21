# ======================================================================================================================
#        File:  config.py
#     Project:  B Bug Tracker
# Description:  Simple bug tracker
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022-2023 Jared Julien <jaredjulien@exsystems.net>
# ---------------------------------------------------------------------------------------------------------------------
"""Config commands for b."""

# ======================================================================================================================
# Import Statements
# ----------------------------------------------------------------------------------------------------------------------
import click
from rich import print




# ======================================================================================================================
# Configuration Subcommands
# ----------------------------------------------------------------------------------------------------------------------
@click.group()
def config():
    """Change configuration settings for b."""


# ----------------------------------------------------------------------------------------------------------------------
@config.command()
@click.argument('key')
@click.pass_context
def unset(ctx: click.Context, key):
    """Remove the saved setting identified by KEY.

    This restores the setting to it's default value.

    To list the current settings, issue the "config list" command.
    """
    ctx.obj['settings'].unset(key)
    ctx.obj['settings'].store()


# ----------------------------------------------------------------------------------------------------------------------
@config.command()
@click.pass_context
def set(ctx: click.Context, key: str, value: str):
    """Set the setting identified by KEY to the provided VALUE."""
    ctx.obj['settings'].set(key, value)
    print(f'"{key}" set to "{value}"')
    ctx.obj['settings'].store()


# ----------------------------------------------------------------------------------------------------------------------
@config.command()
@click.argument('key')
@click.pass_context
def get(ctx: click.Context, key: str):
    """Get the current value for the setting identified by KEY."""
    print(key, '=', ctx.obj['settings'].get(key))


# ----------------------------------------------------------------------------------------------------------------------
@config.command()
@click.pass_context
def list(ctx: click.Context):
    """List all of the currently configured settings."""
    if ctx.obj['settings'].exists:
        print(f"Config file is located at {ctx.obj['settings'].file}")
    else:
        print('All settings are currently defaults')

    for key, value in ctx.obj['settings'].list():
        print(f'{key}={value}')
        # TODO: Indicate which settings are defaults.




# End of File
