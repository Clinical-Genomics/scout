import logging

import click
from flask.cli import with_appcontext

from scout.constants import DATE_DAY_FORMATTER
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("panels", short_help="Display gene panels")
@click.option("-i", "--institute", help="institute id")
@with_appcontext
def panels(institute):
    """Show all gene panels in the database"""
    LOG.info("Running scout view panels")
    adapter = store

    panel_objs = [
        panel for panel in adapter.gene_panels(institute_id=institute, include_hidden=True)
    ]
    if len(panel_objs) == 0:
        LOG.info("No panels found")
        raise click.Abort()
    click.echo("#panel_name\tversion\tnr_genes\thidden\tdate")

    for panel_obj in panel_objs:
        click.echo(
            "{0}\t{1}\t{2}\t{3}\t{4}".format(
                panel_obj["panel_name"],
                str(panel_obj["version"]),
                len(panel_obj["genes"]),
                panel_obj.get("hidden", False),
                str(panel_obj["date"].strftime(DATE_DAY_FORMATTER)),
            )
        )
