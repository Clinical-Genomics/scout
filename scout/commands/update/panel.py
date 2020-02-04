import logging

import click
from flask.cli import with_appcontext

from scout.utils.date import get_date
from scout.update.panel import update_panel
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("panel", short_help="Update a panel")
@click.option("--panel", "-p", help="Specify what panel to update", required=True)
@click.option(
    "--version",
    type=float,
    help="Specify the version of a panel. If no version the latest panel is chosen.",
)
@click.option(
    "--update-date",
    "-d",
    # There will be more roles in the future
    help="Update the date for a panel",
)
@click.option("--update-version", type=float, help="Change the version of a panel")
@with_appcontext
def panel(panel, version, update_date, update_version):
    """
    Update a panel in the database
    """
    adapter = store

    # Check that the panel exists
    panel_obj = adapter.gene_panel(panel, version=version)

    if not panel_obj:
        LOG.warning("Panel %s (version %s) could not be found" % (panel, version))
        click.Abort()

    date_obj = None
    if update_date:
        try:
            date_obj = get_date(update_date)
        except Exception as err:
            LOG.warning(err)
            click.Abort()

    update_panel(
        adapter,
        panel,
        panel_version=panel_obj["version"],
        new_version=update_version,
        new_date=date_obj,
    )
