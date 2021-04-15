import logging

import click
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("diseases", short_help="Display all diseases")
@with_appcontext
def diseases():
    """Show all diseases in the database"""
    LOG.info("Running scout view diseases")
    adapter = store

    disease_objs = adapter.disease_terms()

    nr_diseases = len(disease_objs)
    if nr_diseases == 0:
        click.echo("No diseases found")
    else:
        click.echo("Disease")
        for disease_obj in adapter.disease_terms():
            click.echo("{0}".format(disease_obj["_id"]))
        LOG.info("{0} diseases found".format(nr_diseases))
