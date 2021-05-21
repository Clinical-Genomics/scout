import logging

import click
from bson.json_util import dumps
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("hpo", short_help="Display hpo terms")
@click.option("--term", "-t", help="Search for a single hpo term")
@click.option("--description", "-d", help="Search for hpo terms with a description")
@click.option("--json", "-j", is_flag=True, help="Export terms in json format")
@with_appcontext
def hpo(term, description, json):
    """Show all hpo terms in the database"""
    LOG.info("Running scout view hpo")
    adapter = store
    hpo_terms = None
    if term:
        term = term.upper()
        if not term.startswith("HP:"):
            while len(term) < 7:
                term = "0" + term
            term = "HP:" + term
        LOG.info("Searching for term %s", term)
        hpo_terms = adapter.hpo_terms(hpo_term=term)

    if description:
        hpo_terms = adapter.hpo_terms(query=description)

    if hpo_terms is None:
        hpo_terms = adapter.hpo_terms()

    click.echo("hpo_id\tdescription\tnr_genes")
    if json:
        click.echo(dumps(hpo_terms))
        return

    i = 0
    for i, hpo_obj in enumerate(hpo_terms, 1):
        click.echo(
            "{0}\t{1}\t{2}".format(
                hpo_obj["hpo_id"], hpo_obj["description"], len(hpo_obj.get("genes", []))
            )
        )
    LOG.info("Found %s terms", i)
