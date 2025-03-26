"""Code to handle updates of the PANELAPP-GREEN gene panel via scout CLI"""

import logging

import click
from flask.cli import current_app, with_appcontext

from scout.constants.panels import PANELAPPGREEN_DISPLAY_NAME, PANELAPPGREEN_NAME
from scout.load.panelapp import load_panelapp_green_panel
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
@click.option(
    "-s",
    "--signed-off",
    is_flag=True,
    help="Collect genes from signed-off panels only",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force update even if updated panel contains less genes",
)
@click.option("--panel-id", help="Panel ID", default=PANELAPPGREEN_NAME, show_default=True)
@click.option(
    "--panel-display-name",
    help="Panel display name",
    default=PANELAPPGREEN_DISPLAY_NAME,
    show_default=True,
)
@with_appcontext
def panelapp_green(institute, force, signed_off, panel_id, panel_display_name):
    """
    Update the automatically generated PanelApp Green Genes panel in the database.
    """
    LOG.info("Updating/creating the PanelApp Green gene panel")

    institute_obj = store.institute(institute)
    if not institute_obj:
        LOG.warning(
            f"Institute {institute} could not be found in database. Please specify an existing institute"
        )
        raise click.Abort()

    try:
        load_panelapp_green_panel(
            adapter=store,
            institute=institute,
            force=force,
            signed_off=signed_off,
            panel_id=panel_id,
            panel_display_name=panel_display_name,
        )
    except Exception as err:
        LOG.error(err)
        raise click.Abort()
