# -*- coding: utf-8 -*-
import logging

import click
from flask.cli import with_appcontext

from scout.commands.utils import builds_option
from scout.export.panel import export_gene_panels, export_panels
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("panel", short_help="Export gene panels")
@click.argument("panel", nargs=-1, metavar="<panel_name>")
@builds_option
@click.option(
    "--version",
    type=float,
    help="Specify panel version, only works if one panel is provided",
)
@click.option("--bed", help="Export genes in bed like format", is_flag=True)
@with_appcontext
def panel_cmd(panel: str, build: str, bed: bool, version: float):
    """Export gene panels to .bed like format.

    Specify any number of panels on the command line
    """
    LOG.info("Running scout export panel")
    adapter = store

    if not panel:
        LOG.warning("Please provide at least one gene panel")
        raise click.Abort()

    LOG.info("Exporting panels: {}".format(", ".join(panel)))
    if bed:
        if version:
            version = [version]
        lines = export_panels(adapter=adapter, panels=panel, versions=version, build=build)
    else:
        lines = export_gene_panels(adapter=adapter, panels=panel, version=version)
    for line in lines:
        click.echo(line)
