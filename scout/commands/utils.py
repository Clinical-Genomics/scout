"""
commands/utils.py

Helper functions for cli functions

"""

import click

from scout.constants import BUILDS


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


builds_option = click.option(
    "-b", "--build", default="37", show_default=True, type=click.Choice(BUILDS)
)
