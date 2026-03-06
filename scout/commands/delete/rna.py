import click

from scout.server.extensions import store

CASE_RNA_KEYS = [
    "RNAfusion_inspector",
    "RNAfusion_inspector_research",
    "RNAfusion_report",
    "RNAfusion_report_research",
    "gene_fusion_report",
    "gene_fusion_report_research",
    "has_outliers",
    "multiqc_rna",
    "omics_files",
    "rna_delivery_report",
    "rna_genome_build",
]
INDIVIDUAL_RNA_KEYS = [
    "omics_sample_id",
    "rna_alignment_path",
    "rna_coverage_bigwig",
    "splice_junctions_bed",
]


@click.command("rna", short_help="Remove all RNA data from a case")
@click.option("-c", "--case-id", required=True)
@click.option("--yes", "-y", is_flag=True, help="Automatically confirm and do not prompt.")
def rna(case_id, yes):
    """
    Delete all RNA-associated data from a case. This removes RNA information from the case document and related variants.
    The case document will not show any signs of having been modified,
    and no history of these changes will be recorded.
    This command is intended to be used when something has gone wrong and incorrect RNA data has been loaded for a case.
    """
    adapter = store
    case_obj = adapter.case(case_id=case_id)
    if not case_obj:
        click.echo(f"Couldn't find any case in database with ID {case_id}.")
        raise click.Abort()

    if not yes:
        click.confirm(
            "This will permanently delete all RNA-related data from the case. Continue?",
            abort=True,
        )
    removed_keys = set()

    # Remove case-level associated key/values
    for key in CASE_RNA_KEYS:
        if key not in case_obj:
            continue
        removed_keys.add(key)
        case_obj.pop(key, None)

    # Remove individual-level associated key/values
    for ind in case_obj.get("individuals", []):
        for key in INDIVIDUAL_RNA_KEYS:
            if key not in ind:
                continue
            removed_keys.add(f"individual.{key}")
            ind.pop(key)

    adapter.case_collection.find_one_and_replace(
        {"_id": case_obj["_id"]},
        case_obj,
    )

    click.echo(
        f"Updated/removed keys: {', '.join(sorted(removed_keys))}"
        if removed_keys
        else "No matching RNA keys found."
    )

    # Remove outliers variants
    deleted_count = store.omics_variant_collection.delete_many(
        {
            "case_id": case_id,
            "sub_category": {"$in": ["splicing", "expression"]},
        }
    ).deleted_count
    click.echo(f"Deleted {deleted_count} omics variant documents for case {case_id}.")

    # Update variants count in case document
    adapter.case_variants_count(case_id, case_obj["owner"], True)
