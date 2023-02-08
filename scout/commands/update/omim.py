"""Code to handle updates of the OMIM-AUTO gene panel via scout CLI"""
import logging

import click
from flask.cli import current_app, with_appcontext

from scout.server.extensions import store
from scout.utils.handle import get_file_handle
from scout.utils.scout_requests import fetch_mim_files

LOG = logging.getLogger(__name__)


@click.command("omim", short_help="Update omim gene panel")
@click.option("--api-key", help="Specify the api key")
@click.option(
    "--institute",
    help="Specify the owner of the omim panel",
    default="cust002",
    show_default=True,
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
    "-f",
    "--force",
    is_flag=True,
    help="Force update OMIM panel even if no new version of OMIM is available",
)
@with_appcontext
def omim(api_key, institute, genemap2, mim2genes, force):
    """
    Update the automatically generated omim gene panel in the database.
    """
    LOG.info("Running scout update omim")
    adapter = store

    institute_obj = adapter.institute(institute)
    if not institute_obj:
        LOG.info("Institute %s could not be found in database", institute)
        LOG.warning("Please specify an existing institute")
        raise click.Abort()

    mim_files = None
    if genemap2 and mim2genes:
        mim_files = {
            "genemap2": list(get_file_handle(genemap2)),
            "mim2genes": list(get_file_handle(mim2genes)),
        }

    api_key = api_key or current_app.config.get("OMIM_API_KEY")
    if not api_key and mim_files is None:
        LOG.warning("Please provide a omim api key to load the omim gene panel")
        raise click.Abort()

    if not mim_files:
        try:
            mim_files = fetch_mim_files(api_key=api_key, genemap2=True, mim2genes=True)
        except Exception as err:
            raise err

    try:
        adapter.load_omim_panel(
            genemap2_lines=mim_files["genemap2"],
            mim2gene_lines=mim_files["mim2genes"],
            institute=institute,
            force=force,
        )
    except Exception as err:
        LOG.error(err)
        raise click.Abort()
