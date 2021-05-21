import logging

import click
from flask.cli import with_appcontext

from scout.build.variant import build_variant_evaluation_terms
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("evaluation-terms", short_help="Display evaluation terms")
@click.option("-i", "--institute-id", help="Limit output to institute exclusive")
@click.option("-c", "--term_category", help="Limit output to specific evaluation terms")
@click.option(
    "-t", "--track", default="all", help="Limit the term to a given analysis track"
)
@with_appcontext
def evaluation_terms(institute_id, term_category, track):
    """Show all institutes in the database"""
    LOG.info("Running scout view institutes")
    adapter = store

    query = {}
    if institute_id:
        query["institute"] = institute_id

    if term_category:
        query["term_category"] = term_category

    if track:
        query["track"] = track

    result = adapter.evaluation_terms_collection.find(query)
    term_objs = build_variant_evaluation_terms(result)
    if len(term_objs) == 0:
        click.echo("No evaluation terms found")
        raise click.Abort()

    for term in term_objs:
        row = ""
        for value in term.values():
            row = row + "{0}\t".format(value)

        click.echo(row)
