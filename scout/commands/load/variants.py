import logging
from pprint import pprint as pp

import click
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command(short_help="Upload variants to existing case")
@click.argument("case-id")
@click.option("-i", "--institute", help="institute id of related cases")
@click.option("--cancer", is_flag=True, help="Upload clinical cancer variants")
@click.option("--cancer-research", is_flag=True, help="Upload research cancer variants")
@click.option("--cancer-sv", is_flag=True, help="Upload clinical cancer structural variants")
@click.option(
    "--cancer-sv-research",
    is_flag=True,
    help="Upload research cancer structural variants",
)
@click.option("--sv", is_flag=True, help="Upload clinical structural variants")
@click.option("--sv-research", is_flag=True, help="Upload research structural variants")
@click.option("--snv", is_flag=True, help="Upload clinical SNV variants")
@click.option("--snv-research", is_flag=True, help="Upload research SNV variants")
@click.option("--str-clinical", is_flag=True, help="Upload clinical STR variants")
@click.option("--chrom", help="If region, specify the chromosome")
@click.option("--start", type=int, help="If region, specify the start")
@click.option("--end", type=int, help="If region, specify the end")
@click.option("--hgnc-id", type=int, help="If all variants from a gene, specify the gene id")
@click.option("--hgnc-symbol", help="If all variants from a gene, specify the gene symbol")
@click.option(
    "--rank-treshold",
    default=5,
    help="Specify the rank score treshold",
    show_default=True,
)
@click.option("-f", "--force", is_flag=True, help="upload without request")
@click.option(
    "--keep-actions/--no-keep-actions",
    default=True,
    help="Export user actions from old variants to the new",
)
@with_appcontext
def variants(
    case_id,
    institute,
    cancer,
    cancer_sv,
    cancer_research,
    cancer_sv_research,
    sv,
    sv_research,
    snv,
    snv_research,
    str_clinical,
    chrom,
    start,
    end,
    hgnc_id,
    hgnc_symbol,
    rank_treshold,
    force,
    keep_actions,
):
    """Upload variants to a case

    Note that the files has to be linked with the case,
    if they are not use 'scout update case'.
    """
    LOG.info("Running scout load variants")
    adapter = store

    if institute:
        case_id = "{0}-{1}".format(institute, case_id)
    else:
        institute = case_id.split("-")[0]
    case_obj = adapter.case(case_id=case_id)
    if case_obj is None:
        LOG.info("No matching case found")
        raise click.Abort()

    institute_obj = adapter.institute(case_obj["owner"])
    if not institute_obj:
        LOG.info("Institute %s does not exist", case_obj["owner"])
        raise click.Abort()

    files = [
        {"category": "cancer", "variant_type": "clinical", "upload": cancer},
        {"category": "cancer_sv", "variant_type": "clinical", "upload": cancer_sv},
        {"category": "cancer", "variant_type": "research", "upload": cancer_research},
        {
            "category": "cancer_sv",
            "variant_type": "research",
            "upload": cancer_sv_research,
        },
        {"category": "sv", "variant_type": "clinical", "upload": sv},
        {"category": "sv", "variant_type": "research", "upload": sv_research},
        {"category": "snv", "variant_type": "clinical", "upload": snv},
        {"category": "snv", "variant_type": "research", "upload": snv_research},
        {"category": "str", "variant_type": "clinical", "upload": str_clinical},
    ]

    gene_obj = None
    if hgnc_id or hgnc_symbol:
        if hgnc_id:
            gene_obj = adapter.hgnc_gene(hgnc_id, case_obj["genome_build"])
        if hgnc_symbol:
            for res in adapter.gene_by_alias(hgnc_symbol, case_obj["genome_build"]):
                gene_obj = res
        if not gene_obj:
            LOG.warning("The gene could not be found")
            raise click.Abort()

    old_sanger_variants = adapter.case_sanger_variants(case_obj["_id"])
    old_evaluated_variants = None  # acmg, manual rank, cancer tier, dismissed, mosaic, commented

    if keep_actions:  # collect all variants with user actions for this case
        old_evaluated_variants = list(adapter.evaluated_variants(case_id))

    i = 0
    for file_type in files:
        variant_type = file_type["variant_type"]
        category = file_type["category"]

        if not file_type["upload"]:
            continue

        i += 1
        if variant_type == "research":
            if not (force or case_obj["research_requested"]):
                LOG.warning("research not requested, use '--force'")
                raise click.Abort()

        LOG.info("Delete {0} {1} variants for case {2}".format(variant_type, category, case_id))

        adapter.delete_variants(
            case_id=case_obj["_id"], variant_type=variant_type, category=category
        )

        LOG.info("Load {0} {1} variants for case {2}".format(variant_type, category, case_id))

        try:
            adapter.load_variants(
                case_obj=case_obj,
                variant_type=variant_type,
                category=category,
                rank_threshold=rank_treshold,
                chrom=chrom,
                start=start,
                end=end,
                gene_obj=gene_obj,
                build=case_obj["genome_build"],
            )
            # Update case variants count
            adapter.case_variants_count(case_obj["_id"], case_obj["owner"], force_update_case=True)

        except Exception as e:
            LOG.warning(e)
            raise click.Abort()

    if i == 0:
        LOG.info("No files where specified to upload variants from")
        return

    # update Sanger status for the new inserted variants
    sanger_updated = adapter.update_case_sanger_variants(
        institute_obj, case_obj, old_sanger_variants
    )

    if keep_actions and old_evaluated_variants:
        adapter.update_variant_actions(institute_obj, case_obj, old_evaluated_variants)
