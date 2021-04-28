"""CLI for adding a new evalution term to the database."""
import logging

import click
from flask.cli import with_appcontext

from scout.load import load_evaluation_term
from scout.server.extensions import store
import json

LOG = logging.getLogger(__name__)


@click.command("evaluation-term", short_help="Load a variant evaluation term")
@click.option("-i", "--internal-id")
@click.option("-l", "--label")
@click.option("-n", "--institute")
@click.option("-d", "--description")
@click.option("-c", "--category", help="Type of evaluation term")
@click.option("-a", "--analysis_type", default='all')
@click.option("-e", "--evidence", multiple=True)
@click.option(
    "-r", "--rank", type=int, help="Rank used for determening the order entries are displayed"
)
@click.option(
    "-f", "--file", type=click.File(), help="Load a json file with multiple evaluation terms"
)
@with_appcontext
def evaluation_term(internal_id, institute, label, description, category, analysis_type, evidence, rank, file):
    """Create a new evalution term and add it to the database."""
    adapter = store

    try:
        if file:
            for entry in json.load(file):
                load_evaluation_term(adapter, **entry)
        else:
            if not label:
                label = internal_id

                load_evaluation_term(
                    adapter=adapter,
                    term_categroy=category,
                    type=analysis_type,
                    internal_id=internal_id,
                    institute=institute,
                    label=label,
                    description=description,
                    evidence=evidence,
                    rank=rank,
                )
    except Exception as e:
        LOG.warning(e)
        raise click.Abort()
