"""Code for updating information on individuals
"""
from pathlib import Path

import click

from scout.server.extensions import store

UPDATE_DICT = {
    "bam_file": "path",
    "bionano_access.sample": "str",
    "bionano_access.project": "str",
    "d4_file": "path",
    "chromograph_images.autozygous": "str",
    "chromograph_images.coverage": "str",
    "chromograph_images.upd_regions": "str",
    "chromograph_images.upd_sites": "str",
    "mt_bam": "path",
    "reviewer.alignment": "path",
    "reviewer.alignment_index": "path",
    "reviewer.vcf": "path",
    "reviewer.catalog": "path",
    "rhocall_bed": "path",
    "rhocall_wig": "path",
    "rna_alignment_path": "path",
    "rna_coverage_bigwig": "path",  # Coverage islands generated from bam or cram files (RNA-seq analysis)
    "splice_junctions_bed": "path",  # An indexed junctions .bed.gz file obtained from STAR v2 aligner *.SJ.out.tab file.
    "subject_id": "str",  # Individual subject_id (for matching multiomics data and statistics)
    "tiddit_coverage_wig": "path",
    "upd_regions_bed": "path",
    "upd_sites_bed": "path",
    "vcf2cytosure": "path",
}
UPDATE_KEYS = UPDATE_DICT.keys()


@click.command()
@click.option("--case-id", "-c", required=True, help="Case id")
@click.option("--ind", "-n", help="Individual display name")
@click.argument("key", required=False)
@click.argument("value", required=False)
def individual(case_id, ind, key, value):
    """Update information on individual level in Scout

    UPDATE_DICT holds keys and type of value. If the value type is "path", and most are, a check
    for file existence is performed.

    If the key contains a dot (only one needed currently), keys for a dict type value is assumed:
    e.g. "reviewer.alignment" -> ind["reviewer"]["alignment"] (path value required)

    """

    case_obj = store.case(case_id)
    if not case_obj:
        click.echo(f"Could not find case {case_id}")
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
            f"Could not find individual '{ind}' in case individuals. Available individuals for this case: {list(individuals.keys())}"
        )
        return
    # If key is null or non-valid, print a list of all the keys that can be updated using this function
    if key is None or not key in UPDATE_KEYS:
        click.echo(f"Please specify a valid key to update. Valid keys:{ UPDATE_KEYS }")
        return

    if value is None:
        click.echo(f"Please specify a value ({UPDATE_DICT[key]} for key {key}")
        return
    if UPDATE_DICT[key] == "path":
        file_path = Path(value)
        # If file is not found on the server, ask if user wants to update the key anyway
        if file_path.exists() is False:
            click.confirm(
                "The provided path was not found on the server, update key anyway?",
                abort=True,
            )

    # perform the update. Note that the keys that dig into dictionaries may have a parent exist and be None.
    for ind_obj in case_obj["individuals"]:
        if ind_obj["display_name"] == ind:
            if "." in key:
                key_parts = key.split(".")
                if not ind_obj.get(key_parts[0]):
                    ind_obj[key_parts[0]] = {}
                ind_obj[key_parts[0]][key_parts[1]] = value
                continue

            ind_obj[key] = value

    store.update_case(case_obj)
