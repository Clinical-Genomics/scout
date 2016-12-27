#!/usr/bin/env python
# encoding: utf-8
"""
wipe_database.py

Cli to clean the database.

Created by Måns Magnusson on 2015-01-14.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.

"""

import logging
import click

logger = logging.getLogger(__name__)


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@click.command('wipe', short_help="Wipe a scout instance")
@click.option("--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Are you sure you want to drop the db?"
)
@click.pass_context
def wipe(ctx):
    """Drop the mongo database given."""
    logger.info("Running wipe_mongo")
    ctx.obj['adapter'].drop_database()
    logger.info("Dropped all tables")
