"""Code for scout load panel CLI functionality"""
import logging

import click
from flask.cli import current_app, with_appcontext

from scout.load.panel import load_omim_panel, load_panel, load_panelapp_panel
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("panel", short_help="Load a gene panel")
@click.argument("path", type=click.Path(exists=True), required=False)
@click.option("--panel-id", help="The panel identifier name")
@click.option("--institute", help="Specify the owner of the panel. Defaults to cust000.")
@click.option(
    "--maintainer",
    help="Specify the maintainer user id of the panel. Defaults to empty (all users can edit).",
)
@click.option("-d", "--date", help="date of gene panel on format 2017-12-24, default is today.")
@click.option("-n", "--display-name", help="display name for the panel, optional")
@click.option("-v", "--version", type=float)
@click.option(
    "-t",
    "--panel-type",
    default="clinical",
    show_default=True,
    type=click.Choice(["clinical", "research"]),
)
@click.option(
    "--genemap2",
    type=click.Path(exists=True),
    help="Path to file in omim genemap2 format",
)
@click.option(
    "--mim2genes",
    type=click.Path(exists=True),
    help="Path to file in omim mim2genes format",
)
@click.option(
    "--omim",
    is_flag=True,
    help=(
        "Load the OMIM-AUTO panel into scout."
        "An OMIM api key is required to do this(https://omim.org/api)."
    ),
)
@click.option("--api-key", help="A OMIM api key, see https://omim.org/api.")
@click.option("--panel-app", is_flag=True, help="Load all PanelApp panels into scout.")
@click.option(
    "--panel-app-confidence",
    type=click.Choice(
        ["green", "amber", "red"],
        case_sensitive=True,
    ),
)
@with_appcontext
def panel(
    path,
    date,
    display_name,
    version,
    panel_type,
    panel_id,
    institute,
    maintainer,
    omim,
    genemap2,
    mim2genes,
    api_key,
    panel_app,
    panel_app_confidence,
):
    """Add a gene panel to the database."""

    adapter = store
    institute = institute or "cust000"

    if omim:
        load_omim_panel(adapter, genemap2, mim2genes, api_key, institute)
        return

    if panel_app:
        load_panelapp_panel(
            adapter, panel_id, institute=institute, confidence=panel_app_confidence or "green"
        )
        return

    if path is None:
        LOG.info("Please provide a panel")
        return
    try:
        load_panel(
            panel_path=path,
            adapter=adapter,
            date=date,
            display_name=display_name,
            version=version,
            panel_type=panel_type,
            panel_id=panel_id,
            institute=institute,
            maintainer=maintainer,
        )
    except Exception as err:
        LOG.warning(err)
        raise click.Abort()
