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
@click.option(
    "--add-maintainer",
    "-a",
    # There will be more roles in the future
    help="Add a maintainter user_id for a panel",
)
@click.option(
    "--revoke-maintainer",
    "-r",
    # There will be more roles in the future
    help="Revoke maintainter status for user_id for a panel",
)
@click.option("--update-version", type=float, help="Change the version of a panel")
@with_appcontext
def panel(panel, version, update_date, update_version, add_maintainer, revoke_maintainer):
    """
    Update a panel in the database
    """
    adapter = store

    # Check that the panel exists
    panel_obj = adapter.gene_panel(panel, version=version)

    if not panel_obj:
        LOG.warning("Panel %s (version %s) could not be found", panel, version)
        raise click.Abort()

    date_obj = None
    if update_date:
        try:
            date_obj = get_date(update_date)
        except Exception as err:
            LOG.warning(err)
            raise click.Abort()

    # Any mintainer updates?

    new_maintainer = None
    if add_maintainer:
        user_obj = adapter.user(user_id=add_maintainer)
        if not user_obj:
            # Check if maintainers exist in the user database
            LOG.warning("Maintainer user id %s does not exist in user database", add_maintainer)

            raise click.Abort()

        new_maintainer = panel_obj.get("maintainer") or []
        if add_maintainer in new_maintainer:
            LOG.warning("User %s already in maintainer list.", add_maintainer)
            raise click.Abort()

        new_maintainer.append(add_maintainer)

    if revoke_maintainer:
        current_maintainers = panel_obj.get("maintainer") or []
        try:
            current_maintainers.remove(revoke_maintainer)
            new_maintainer = current_maintainers
        except ValueError:
            LOG.warning(
                "Maintainer user id %s is not a maintainer for panel %s. Current maintainers: %s",
                revoke_maintainer,
                panel,
                current_maintainers,
            )

    update_panel(
        adapter,
        panel,
        panel_version=panel_obj["version"],
        new_version=update_version,
        new_maintainer=new_maintainer,
        new_date=date_obj,
    )
