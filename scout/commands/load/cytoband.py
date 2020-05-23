# -*- coding: utf-8 -*-
import click
from flask.cli import with_appcontext
import logging
from scout.load.cytoband import load_cytobands
from scout.resources import cytoband_files
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("cytobands", short_help="Load cytobands")
@click.option(
    "--build",
    type=click.Choice(["37", "38"]),
    help="What genome build should be used. If no choice update 37 and 38.",
)
@with_appcontext
def cytoband(build):
    """Populate cytobands collection

    Args:
        build(str): "37" or "38"
    """
    resources = []
    # setting up resource files
    if build is not None:
        for resource in cytoband_files:
            if resource["build"] == build:
                resources.append(resource)
    else:
        resources = cytoband_files

    click.echo(f"{resources}")

    # Remove previous cytoband objects from cytoband collection
    store.cytoband_collection.delete_many({})

    # Load cytobands
    for resource in resources:
        load_cytobands(resource["path"], resource["build"], store)
