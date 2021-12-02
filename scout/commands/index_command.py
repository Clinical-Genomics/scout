import logging
import sys

import click
from flask.cli import with_appcontext

from scout.constants import INDEXES
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
    prompt="This will delete and rebuild indexes(if not --update) for the given collections (or the whole database). Are you sure?",
)
@click.option("--update", help="Update the indexes", is_flag=True)
@click.option(
    "-c", "--collection", multiple=True, help="Name of collection to update/rebuild the indexes for"
)
@with_appcontext
def index(update, collection):
    """Create indexes for the database"""
    LOG.info("Running scout index")
    adapter = store

    for collx in collection:
        if collx in INDEXES:
            continue
        sys.exit(f"Collection '{collx}' not found in database")

    if update:
        adapter.update_indexes(collection)
    else:
        adapter.load_indexes(collection)
