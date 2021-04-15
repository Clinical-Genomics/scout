# -*- coding: utf-8 -*-
import click
from flask.cli import with_appcontext

from scout.load.cytoband import load_cytobands
from scout.resources import cytoband_files
from scout.server.extensions import store


@click.command("cytobands", short_help="Load cytobands")
@click.option(
    "--build",
    type=click.Choice(["37", "38"]),
    help="What genome build should be loaded. If no choice update 37 and 38.",
)
@with_appcontext
def cytoband(build):
    """Populate cytobands collection

    Args:
        build(str): "37" or "38"
    """
    # Remove previous cytoband objects from cytoband collection
    store.cytoband_collection.drop()

    if build is None:
        builds = cytoband_files.keys()
    else:
        builds = [build]
    # Look cytobands for each chromosome build
    for genome_build in builds:
        resource_path = cytoband_files.get(genome_build)
        load_cytobands(resource_path, genome_build, store)
