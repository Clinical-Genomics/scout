"""Code for updating information on individuals"""
from pathlib import Path

import click
from scout.constants import INDIVIDUAL_UPDATE_OPTIONS
from scout.server.extensions import store

UPDATE_KEYS = {
    "bam_file": {"help": "Path to BAM/CRAM alignment file", "type": Path},
    "mt_bam": {"help": "Path to reduced MT BAM/CRAM alignment file", "type": Path},
    "vcf2cytosure": {"help": "Path to vcf2cytosure .cgh file", "type": Path},
    "rhocall_bed": {"help": "Path to Rhocall bed file", "type": Path},
    "rhocall_wig": {"help": "Path to Rhocall wig file", "type": Path},
    "tiddit_coverage_wig": {"help": "Path to Tiddit coverage wig file", "type": Path},
    "upd_regions_bed": {"help": "Path to UPD regions bed file", "type": Path},
    "upd_sites_bed": {"help": "Path to UPD sites bed file", "type": Path},
}


@click.command()
@click.option("--case-id", "-c", required=True, help="Case id")
@click.option("--ind", "-n", help="Individual display name")
@click.argument("key", required=False)
@click.argument("value", required=False)
def individual(case_id, ind, key, value):
    """Update information on individual level in Scout"""

    case_obj = store.case(case_id)
    if not case_obj:
        click.echo("Could not find case %s", case_id)
        return
    individuals = {ind_info["display_name"]: ind_info for ind_info in case_obj["individuals"]}
    # If ind name is empty, print available individual names for this case to help the user to build the command
    if ind is None:
        click.echo(
            f"Please specify individual name with '-n' option. Available individuals for this case:{list(individuals.keys())}"
        )
        return
    if ind not in individuals:
        click.echo(
            f"Could not find individual '{ind_name}' in case individuals. Available individuals for this case: {list(individuals.keys)}"
        )
        return
    # If key is null or non-valid, print a list of all the keys that can be updated using this function
    if key is None or not key in UPDATE_KEYS:
        click.echo(f"Please specify a valid key to update. Valid keys:{ list(UPDATE_KEYS.keys()) }")
        return
    if value is None:
        click.echo(f"Please specify a file path for key {key}")
    file_path = Path(value)
    # If file os not found on the server, ask user if they want to update key anyway
    if file_path.exists() is False:
        click.confirm(
            "The provided path was not found on the server, update key anyway?", abort=True
        )

    # perform the update
    for ind_obj in case_obj["individuals"]:
        if ind_obj["display_name"] == ind:
            ind_obj[key] = value

    store.update_case(case_obj)
