import logging
from pprint import pprint as pp

import click
import pymongo
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("case", short_help="Update a case")
@click.argument("case_id", required=False)
@click.option("--case-name", "-n", help="Add/update the display name of case")
@click.option("--institute", "-i", help="Update what institutes that has access to case")
@click.option("--collaborator", "-c", help="Add a collaborator to the case")
@click.option("--vcf", type=click.Path(exists=True), help="path to clinical VCF file to be added")
@click.option(
    "--vcf-sv",
    type=click.Path(exists=True),
    help="path to clinical SV VCF file to be added",
)
@click.option(
    "--vcf-cancer",
    type=click.Path(exists=True),
    help="path to clinical cancer VCF file to be added",
)
@click.option(
    "--vcf-cancer-sv",
    type=click.Path(exists=True),
    help="path to clinical cancer structural VCF file to be added",
)
@click.option(
    "--vcf-research",
    type=click.Path(exists=True),
    help="path to research VCF file to be added",
)
@click.option(
    "--vcf-sv-research",
    type=click.Path(exists=True),
    help="path to research VCF with SV variants to be added",
)
@click.option(
    "--vcf-cancer-research",
    type=click.Path(exists=True),
    help="path to research VCF with cancer variants to be added",
)
@click.option(
    "--vcf-cancer-sv-research",
    type=click.Path(exists=True),
    help="path to research VCF with cancer structural variants to be added",
)
@click.option(
    "--reupload-sv",
    is_flag=True,
    help="Remove all SVs and re upload from existing files",
)
@click.option("--rankscore-treshold", help="Set a new rank score treshold if desired")
@click.option("--rankmodel-version", help="Update the rank model version")
@click.option("--sv-rankmodel-version", help="Update the SV rank model version")
@click.pass_context
def case(
    context,
    case_id,
    case_name,
    institute,
    collaborator,
    vcf,
    vcf_sv,
    vcf_cancer,
    vcf_cancer_sv,
    vcf_research,
    vcf_sv_research,
    vcf_cancer_research,
    vcf_cancer_sv_research,
    reupload_sv,
    rankscore_treshold,
    rankmodel_version,
    sv_rankmodel_version,
):
    """
    Update a case in the database
    """
    adapter = store
    if not case_id:
        if not (case_name and institute):
            LOG.info("Please specify which case to update.")
            raise click.Abort()
        case_id = "{0}-{1}".format(institute, case_name)
    # Check if the case exists
    case_obj = adapter.case(case_id)

    if not case_obj:
        LOG.warning("Case %s could not be found", case_id)
        context.abort()

    case_changed = False
    if collaborator:
        if not adapter.institute(collaborator):
            LOG.warning("Institute %s could not be found", collaborator)
            return
        if not collaborator in case_obj["collaborators"]:
            case_changed = True
            case_obj["collaborators"].append(collaborator)
            LOG.info("Adding collaborator %s", collaborator)

    if vcf:
        LOG.info("Updating 'vcf_snv' to %s", vcf)
        case_obj["vcf_files"]["vcf_snv"] = vcf
        case_changed = True
    if vcf_sv:
        LOG.info("Updating 'vcf_sv' to %s", vcf_sv)
        case_obj["vcf_files"]["vcf_sv"] = vcf_sv
        case_changed = True
    if vcf_cancer:
        LOG.info("Updating 'vcf_cancer' to %s", vcf_cancer)
        case_obj["vcf_files"]["vcf_cancer"] = vcf_cancer
        case_changed = True
    if vcf_cancer_sv:
        LOG.info("Updating 'vcf_cancer_sv' to %s", vcf_cancer_sv)
        case_obj["vcf_files"]["vcf_cancer_sv"] = vcf_cancer_sv
        case_changed = True
    if vcf_research:
        LOG.info("Updating 'vcf_research' to %s", vcf_research)
        case_obj["vcf_files"]["vcf_research"] = vcf_research
        case_changed = True
    if vcf_sv_research:
        LOG.info("Updating 'vcf_sv_research' to %s", vcf_sv_research)
        case_obj["vcf_files"]["vcf_sv_research"] = vcf_sv_research
        case_changed = True
    if vcf_cancer_research:
        LOG.info("Updating 'vcf_cancer_research' to %s", vcf_cancer_research)
        case_obj["vcf_files"]["vcf_cancer_research"] = vcf_cancer_research
        case_changed = True
    if vcf_cancer_sv_research:
        LOG.info("Updating 'vcf_cancer_sv_research' to %s", vcf_cancer_sv_research)
        case_obj["vcf_files"]["vcf_cancer_sv_research"] = vcf_cancer_sv_research
        case_changed = True

    if case_changed:
        adapter.update_case(case_obj)

    if reupload_sv:
        LOG.info("Set needs_check to True for case %s", case_id)
        updates = {"needs_check": True}
        if sv_rankmodel_version:
            updates["sv_rank_model_version"] = sv_rankmodel_version
        if vcf_sv:
            updates["vcf_files.vcf_sv"] = vcf_sv
        if vcf_sv:
            updates["vcf_files.vcf_sv_research"] = vcf_sv_research

        updated_case = adapter.case_collection.find_one_and_update(
            {"_id": case_id},
            {"$set": updates},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        rankscore_treshold = rankscore_treshold or updated_case.get("rank_score_threshold", 5)
        # Delete and reload the clinical SV variants
        if updated_case["vcf_files"].get("vcf_sv"):
            adapter.delete_variants(case_id, variant_type="clinical", category="sv")
            adapter.load_variants(
                updated_case,
                variant_type="clinical",
                category="sv",
                rank_threshold=int(rankscore_treshold),
            )
        # Delete and reload research SV variants
        if updated_case["vcf_files"].get("vcf_sv_research"):
            adapter.delete_variants(case_id, variant_type="research", category="sv")
            if updated_case.get("is_research"):
                adapter.load_variants(
                    updated_case,
                    variant_type="research",
                    category="sv",
                    rank_threshold=int(rankscore_treshold),
                )
        # Update case variants count
        adapter.case_variants_count(case_obj["_id"], case_obj["owner"], force_update_case=True)
