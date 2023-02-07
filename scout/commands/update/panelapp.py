"""Code to handle updates of the PANELAPP-GREEN gene panel via scout CLI"""
import logging

import click
from flask.cli import current_app, with_appcontext

from scout.load.panel import load_panelapp_green_panel
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("panelapp-green", short_help="Update/create the PanelApp Green genes panel")
@click.option(
    "-i",
    "--institute",
    help="Specify the owner of the omim panel",
    default="cust002",
    show_default=True,
)
@with_appcontext
def panelapp_green(institute):
    """
    Update the automatically generated omim gene panel in the database.
    """
    LOG.info("Updating/Creating the PanelApp green gene panel")

    institute_obj = store.institute(institute)
    if not institute_obj:
        LOG.warning(
            f"Institute {institute} could not be found in database. Please specify an existing institute"
        )
        raise click.Abort()

    try:
        load_panelapp_green_panel(adapter=store, institute=institute)
    except Exception as err:
        LOG.error(err)
        raise click.Abort()
