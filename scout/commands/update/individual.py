"""Code for updating information on individuals"""
import logging
import pathlib

import click

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command()
@click.option("--case-id", "-c", required=True, help="Case id")
@click.option("--ind-name", "-n", required=True, help="Individual display name")
@click.option(
    "--alignment-path",
    "-a",
    type=click.Path(exists=True),
    help="Replace alignment file",
)
def individual(case_id, ind_name, alignment_path):
    """Update information on individual level in Scout"""
    adapter = store
    case_obj = adapter.case(case_id)
    if not case_obj:
        LOG.warning("Could not find case %s", case_id)
        return
    individuals = {ind_info["individual_id"]: ind_info for ind_info in case_obj["individuals"]}
    if ind_name not in individuals:
        LOG.warning("Could not find individual %s in case %s", ind_name, case_id)
        return

    case_changed = False
    for ind_info in case_obj["individuals"]:
        if not ind_info["display_name"] == ind_name:
            continue
        """
        if alignment_path:
            alignment_path = pathlib.Path(alignment_path).resolve()
            LOG.info("Updating alignment path for %s to %s", ind_name, alignment_path)
            ind_info["bam_file"] = str(alignment_path)
            case_changed = True
        """

    if not case_changed:
        LOG.info("Nothing to update")
        return

    adapter.update_case(case_obj)
