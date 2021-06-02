"""CLI for adding new evalution terms to the database."""

import logging

import click
from flask.cli import with_appcontext

from scout.constants.case_tags import TRACKS
from scout.load.evaluation_terms import load_default_evaluation_terms
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.group()
def evaluation_terms():
    """Update custom or default evaluation terms"""


@evaluation_terms.command()
@with_appcontext
def default_terms():
    """Test loading default variant evaluation terms into database"""

    click.confirm(
        'This command will replace all evantual variant evaluation terms ("dismissal_term", "manual_rank", "cancer_tier", "mosaicism_options") present in the database with the default ones. Continue?',
        abort=True,
    )
    load_default_evaluation_terms(store)
