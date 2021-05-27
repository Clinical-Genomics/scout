"""CLI for adding new evalution terms to the database."""

import logging

import click
from flask.cli import with_appcontext

from scout.load.evaluation_terms import load_default_evaluation_terms
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command(
    short_help='Load default ("dismissal_term", "manual_rank", "cancer_tier", "mosaicism_options") terms into the database'
)
@with_appcontext
def default_variant_evaluation_terms():
    """Upload default manual rank terms and variant dismissal terms into the database.
    These terms reside in scout.constants.variant_tags.
    """
    click.confirm(
        'This command will replace all evantual variant evaluation terms ("dismissal_term", "manual_rank", "cancer_tier", "mosaicism_options") present in the database with the default ones. Continue?',
        abort=True,
    )
    load_default_evaluation_terms(store)
