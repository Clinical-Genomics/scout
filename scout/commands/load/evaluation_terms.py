"""CLI for adding new evalution terms to the database."""

import logging

import click
from flask.cli import with_appcontext

from scout.load.evaluation_terms import load_custom_evaluation_terms, load_default_evaluation_terms
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.group()
def evaluation_terms():
    """Update custom or default evaluation terms"""


@evaluation_terms.command()
@with_appcontext
def default_terms():
    """Load default variant evaluation terms into database"""

    click.confirm(
        'This command will replace all evantual variant evaluation terms ("dismissal_term", "manual_rank", "cancer_tier", "mosaicism_options") present in the database with the default ones. Continue?',
        abort=True,
    )
    load_default_evaluation_terms(store)


@evaluation_terms.command()
@with_appcontext
@click.option(
    "-f",
    "--file",
    type=click.File(),
    required=True,
    help="Load a python file with multiple evaluation terms",
)
def custom_terms(file):
    """Load custom variant evaluation terms from a json file into database"""

    click.confirm(
        'This command will replace all evantual variant evaluation terms ("dismissal_term", "manual_rank", "cancer_tier", "mosaicism_options") present in the database with the ones found on the provided file. Continue?',
        abort=True,
    )
    load_custom_evaluation_terms(store, file)
