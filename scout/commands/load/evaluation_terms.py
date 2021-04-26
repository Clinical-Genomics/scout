"""CLI for adding a new evalution term to the database."""
import logging

import click
from flask.cli import with_appcontext

from scout.load import load_evaluation_terms
from scout.server.extensions import store

@click.command("evaluation_terms", short_help="Load a variant evaluation term")
@click.option("-i", "--internal-id", required=True)
@click.option("-l", "--label")
@click.option("-a", "--institute")
@click.option("-d", "--description")
@click.option("-e", "--evidence", multiple=True)
@with_appcontext
def evaluation_term(internal_id, institute, label, description, evidence):
    """Create a new evalution term and add it to the database."""
    adapter = store

    if not label:
        label = internal_id

    try:
        load_evaluation_terms(
            adapter=adapter,
            internal_id=internal_id,
            institute=institute,
            label=label,
            description=description,
            evidence=evidence,
        )
    except Exception as e:
        LOG.warning(e)
        raise click.Abort()
