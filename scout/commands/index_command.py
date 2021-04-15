import logging

import click
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@click.command("index", short_help="Index the database")
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="This will delete and rebuild all indexes(if not --update). Are you sure?",
)
@click.option("--update", help="Update the indexes", is_flag=True)
@with_appcontext
def index(update):
    """Create indexes for the database"""
    LOG.info("Running scout index")
    adapter = store

    if update:
        adapter.update_indexes()
    else:
        adapter.load_indexes()
