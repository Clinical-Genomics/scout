#!/usr/bin/env python
# encoding: utf-8
"""
wipe_database.py

CLI to clean the database.

Created by Måns Magnusson on 2015-01-14.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.

"""

import logging
import click

from flask.cli import with_appcontext, current_app

LOG = logging.getLogger(__name__)


def abort_if_false(ctx, param, value):
    if not value:
        raise click.Abort()


@click.command("wipe", short_help="Wipe a scout instance")
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Are you sure you want to drop the db?",
)
@with_appcontext
def wipe():
    """Drop the mongo database given."""
    LOG.info("Running scout wipe")
    db_name = current_app.config["MONGO_DBNAME"]
    LOG.info("Dropping database %s", db_name)
    try:
        current_app.config["MONGO_CLIENT"].drop_database(db_name)
    except Exception as err:
        LOG.warning(err)
        raise click.Abort()
    LOG.info("Dropped whole database")
