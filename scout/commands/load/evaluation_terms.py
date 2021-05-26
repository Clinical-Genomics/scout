"""CLI for adding new evalution terms to the database."""

import logging

import click
from flask.cli import with_appcontext

from scout.load.evaluation_terms import load_default_evaluation_terms
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command(short_help="Load default manual rank and variant dismissal terms into the database")
@with_appcontext
def default_evaluations():
    """Upload default manual rank terms and variant dismissal terms into the database.
    These terms reside in scout.constants.variant_tags.
    """
    load_default_evaluation_terms(store)
