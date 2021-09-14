"""Code for scout load panel CLI functionality"""
import logging

import click
from flask.cli import current_app, with_appcontext

from scout.load.panel import load_panel, load_panel_app
from scout.server.extensions import store
from scout.utils.handle import get_file_handle
from scout.utils.scout_requests import fetch_mim_files

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
):
    """Add a gene panel to the database."""

    adapter = store
    institute = institute or "cust000"

    if omim:
        _panel_omim(adapter, genemap2, mim2genes, api_key, institute)
        return

    if panel_app:
        # try:
        load_panel_app(adapter, panel_id, institute=institute)
        # except Exception as err:
        #     LOG.warning(err)
        #     raise click.Abort()
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

    return


def _panel_omim(adapter, genemap2, mim2genes, api_key, institute):
    """Add OMIM panel to the database.
    Args:
        adapter(scout.adapter.MongoAdapter)
        genemap2(str): Path to file in omim genemap2 format
        mim2genes(str): Path to file in omim mim2genes format
        api_key(str): OMIM API key
        institute(str): institute _id
    """

    mim_files = None
    if genemap2 and mim2genes:
        mim_files = {
            "genemap2": list(get_file_handle(genemap2)),
            "mim2genes": list(get_file_handle(mim2genes)),
        }

    api_key = api_key or current_app.config.get("OMIM_API_KEY")
    if not api_key and mim_files is None:
        LOG.warning(
            "Please provide either an OMIM api key or the path to genemap2 and mim2genesto to load the omim gene panel"
        )
        raise click.Abort()
    # Check if OMIM-AUTO exists
    if adapter.gene_panel(panel_id="OMIM-AUTO"):
        LOG.warning(
            "OMIM-AUTO already exists in database. Use the command 'scout update omim' to create a new OMIM panel version"
        )
        return

    if not mim_files:
        try:
            mim_files = fetch_mim_files(api_key=api_key, genemap2=True, mim2genes=True)
        except Exception as err:
            raise err

    # Here we know that there is no panel loaded
    try:
        adapter.load_omim_panel(
            genemap2_lines=mim_files["genemap2"],
            mim2gene_lines=mim_files["mim2genes"],
            institute=institute,
        )
    except Exception as err:
        LOG.error(err)
        raise click.Abort()
