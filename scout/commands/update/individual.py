"""Code for updating information on individuals"""
import logging
import pathlib

import click

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command()
@click.option("--case-id", "-c", required=True)
@click.option("--ind-id", "-i", required=True)
@click.option(
    "--alignment-path",
    "-a",
    type=click.Path(exists=True),
    help="Replace alignment file",
)
def individual(case_id, ind_id, alignment_path):
    """Update information on individual level in Scout"""
    adapter = store
    case_obj = adapter.case(case_id)
    if not case_obj:
        LOG.warning("Could not find case %s", case_id)
        return
    individuals = {
        ind_info["individual_id"]: ind_info for ind_info in case_obj["individuals"]
    }
    if ind_id not in individuals:
        LOG.warning("Could not find individual %s in case %s", ind_id, case_id)
        return

    case_changed = False
    for ind_info in case_obj["individuals"]:
        if not ind_info["individual_id"] == ind_id:
            continue
        if alignment_path:
            alignment_path = pathlib.Path(alignment_path).resolve()
            LOG.info("Updating alignment path for %s to %s", ind_id, alignment_path)
            ind_info["bam_file"] = str(alignment_path)
            case_changed = True

    if not case_changed:
        LOG.info("Nothing to update")
        return

    adapter.update_case(case_obj)
