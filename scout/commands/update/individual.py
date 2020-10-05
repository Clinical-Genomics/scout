"""Code for updating information on individuals"""
import logging
import pathlib

import click
from scout.constants import INDIVIDUAL_UPDATE_OPTIONS
from scout.server.extensions import store

LOG = logging.getLogger(__name__)
ALLOWED_OPTIONS = ["phenotype", "alignment", "mt_alignment", "vcf2cytosure", "rhocall_bed", "rhocall_wig", "tiddit_coverage", "upd_"]

options = INDIVIDUAL_UPDATE_OPTIONS

@click.command()
@click.option("--case-id", "-c", required=True, help="Case id")
@click.option("--ind", "-n", help="Individual display name")
def individual(case_id, ind):
    """Update information on individual level in Scout"""

    case_obj = store.case(case_id)
    if not case_obj:
        click.echo("Could not find case %s", case_id)
        return
    individuals = {ind_info["display_name"]: ind_info for ind_info in case_obj["individuals"]}
    # If ind_name is empty, print available individual names for this case
    if ind is None:
        click.echo(f"Available individuals for this case:{list(individuals.keys())}")
        return
    if ind not in individuals:
        click.(f"Could not find individual '{ind_name}' in case individuals. Available individuals for this case: {list(individuals.keys()}")
        return


    """



    case_changed = False
    for ind_info in case_obj["individuals"]:
        if not ind_info["display_name"] == ind_name:
            continue

        if alignment_path:
            alignment_path = pathlib.Path(alignment_path).resolve()
            LOG.info("Updating alignment path for %s to %s", ind_name, alignment_path)
            ind_info["bam_file"] = str(alignment_path)
            case_changed = True

    if not case_changed:
        LOG.info("Nothing to update")
        return

    adapter.update_case(case_obj)
    """
