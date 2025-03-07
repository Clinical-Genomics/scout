import logging

import click
import pymongo

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("case", short_help="Update a case")
@click.argument("case_id", required=False)
@click.option(
    "--case-name", "-n", help="Search case by display name (institute ID should also be provided)"
)
@click.option(
    "--institute", "-i", help="Case institute ID (case display name should also be provided)"
)
@click.option("--collaborator", "-c", help="Add a collaborator to the case")
@click.option(
    "--fraser",
    help="Path to clinical WTS OMICS outlier FRASER TSV file to be added - NB variants are NOT loaded",
)
@click.option(
    "--fraser-research",
    help="Path to research WTS OMICS outlier FRASER TSV file to be added - NB variants are NOT loaded",
)
@click.option(
    "--outrider",
    help="Path to clinical WTS OMICS outlier OUTRIDER TSV file to be added - NB variants are NOT loaded",
)
@click.option(
    "--outrider-research",
    help="Path to research WTS OMICS outlier OUTRIDER TSV file to be added - NB variants are NOT loaded",
)
@click.option(
    "--rna-genome-build",
    type=click.Choice(["37", "38"]),
    help="RNA human genome build - should match RNA alignment files and IGV tracks",
)
@click.option(
    "--vcf",
    type=click.Path(exists=True),
    help="Path to clinical VCF file to be added - NB variants are NOT loaded",
)
@click.option(
    "--vcf-sv",
    type=click.Path(exists=True),
    help="path to clinical SV VCF file to be added",
)
@click.option(
    "--vcf-str",
    type=click.Path(exists=True),
    help="Path to clinical STR VCF file to be added - NB variants are NOT loaded",
)
@click.option(
    "--vcf-cancer",
    type=click.Path(exists=True),
    help="Path to clinical cancer VCF file to be added - NB variants are NOT loaded",
)
@click.option(
    "--vcf-cancer-sv",
    type=click.Path(exists=True),
    help="Path to clinical cancer structural VCF file to be added - NB variants are NOT loaded",
)
@click.option(
    "--vcf-research",
    type=click.Path(exists=True),
    help="Path to research VCF file to be added - NB variants are NOT loaded",
)
@click.option(
    "--vcf-sv-research",
    type=click.Path(exists=True),
    help="Path to research VCF with SV variants to be added",
)
@click.option(
    "--vcf-cancer-research",
    type=click.Path(exists=True),
    help="Path to research VCF with cancer variants to be added - NB variants are NOT loaded",
)
@click.option(
    "--vcf-cancer-sv-research",
    type=click.Path(exists=True),
    help="Path to research VCF with cancer structural variants to be added - NB variants are NOT loaded",
)
@click.option(
    "--vcf-mei",
    type=click.Path(exists=True),
    help="Path to clinical mei variants to be added - NB variants are NOT loaded",
)
@click.option(
    "--vcf-mei-research",
    type=click.Path(exists=True),
    help="Path to research mei variants to be added - NB variants are NOT loaded",
)
@click.option(
    "--reupload-sv",
    is_flag=True,
    help="Remove all SVs and re upload from existing files",
)
@click.option("--rankscore-treshold", help="Set a new rank score treshold if desired")
@click.option("--sv-rankmodel-version", help="Update the SV rank model version")
@click.pass_context
def case(
    context,
    case_id,
    case_name,
    institute,
    collaborator,
    fraser,
    fraser_research,
    outrider,
    outrider_research,
    vcf,
    vcf_sv,
    vcf_str,
    vcf_cancer,
    vcf_cancer_sv,
    vcf_research,
    vcf_sv_research,
    vcf_cancer_research,
    vcf_cancer_sv_research,
    vcf_mei,
    vcf_mei_research,
    reupload_sv,
    rankscore_treshold,
    rna_genome_build,
    sv_rankmodel_version,
):
    """
    Update a case in the database
    """

    if not case_id:
        if not (case_name and institute):
            LOG.info(
                "Please specify either a case ID or both case name and institute ID for the case that should be updated."
            )
            raise click.Abort()

    # Check if the case exists
    case_obj = store.case(case_id=case_id, institute_id=institute, display_name=case_name)

    if not case_obj:
        LOG.warning("Case %s could not be found", case_id)
        context.abort()

    case_changed = False
    if collaborator:
        if not store.institute(collaborator):
            LOG.warning("Institute %s could not be found", collaborator)
            return
        if not collaborator in case_obj["collaborators"]:
            case_changed = True
            case_obj["collaborators"].append(collaborator)
            LOG.info("Adding collaborator %s", collaborator)

    for key_name, key in [
        ("vcf_snv", vcf),
        ("vcf_sv", vcf_sv),
        ("vcf_str", vcf_str),
        ("vcf_cancer", vcf_cancer),
        ("vcf_cancer_sv", vcf_cancer_sv),
        ("vcf_research", vcf_research),
        ("vcf_sv_research", vcf_sv_research),
        ("vcf_cancer_research", vcf_cancer_research),
        ("vcf_cancer_sv_research", vcf_cancer_sv_research),
        ("vcf_mei", vcf_mei),
        ("vcf_mei_research", vcf_mei_research),
    ]:
        if key is None:
            continue
        LOG.info(f"Updating '{key_name}' to {key}")
        case_obj["vcf_files"][key_name] = key
        case_changed = True

    for key_name, key in [
        ("fraser", fraser),
        ("fraser_research", fraser_research),
        ("outrider", outrider),
        ("outrider_research", outrider_research),
    ]:
        if key is None:
            continue
        LOG.info(f"Updating '{key_name}' to {key}")

        if "omics_files" not in case_obj or case_obj["omics_files"] is None:
            case_obj["omics_files"] = {}

        case_obj["omics_files"][key_name] = key
        case_obj["has_outliers"] = True
        case_changed = True

    if rna_genome_build:
        case_obj["rna_genome_build"] = rna_genome_build
        case_changed = True

    if case_changed:
        institute_obj = store.institute(case_obj["owner"])
        store.update_case_cli(case_obj, institute_obj)

    if reupload_sv:
        LOG.info("Set needs_check to True for case %s", case_id)
        updates = {"needs_check": True}
        if sv_rankmodel_version:
            updates["sv_rank_model_version"] = str(sv_rankmodel_version)
        if vcf_sv:
            updates["vcf_files.vcf_sv"] = vcf_sv
        if vcf_sv_research:
            updates["vcf_files.vcf_sv_research"] = vcf_sv_research

        updated_case = store.case_collection.find_one_and_update(
            {"_id": case_id},
            {"$set": updates},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        rankscore_treshold = rankscore_treshold or updated_case.get("rank_score_threshold", 5)
        # Delete and reload the clinical SV variants
        if updated_case["vcf_files"].get("vcf_sv"):
            store.delete_variants(case_id, variant_type="clinical", category="sv")
            store.load_variants(
                updated_case,
                variant_type="clinical",
                category="sv",
                rank_threshold=int(rankscore_treshold),
            )
        # Delete and reload research SV variants
        if updated_case["vcf_files"].get("vcf_sv_research"):
            store.delete_variants(case_id, variant_type="research", category="sv")
            if updated_case.get("is_research"):
                store.load_variants(
                    updated_case,
                    variant_type="research",
                    category="sv",
                    rank_threshold=int(rankscore_treshold),
                )
        # Update case variants count
        store.case_variants_count(case_obj["_id"], case_obj["owner"], force_update_case=True)
