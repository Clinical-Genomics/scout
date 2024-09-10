import logging
from typing import Dict, List, Optional

import click
from flask.cli import with_appcontext

from scout.constants import OMICS_FILE_TYPE_MAP
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
@click.option("--mei", is_flag=True, help="Upload clinical MEI variants")
@click.option("--mei-research", is_flag=True, help="Upload research MEI variants")
@click.option("--outlier", is_flag=True, help="Upload clinical OMICS outlier variants")
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
    help="Specify the rank score threshold. Deprecation warning: this parameter name will change in a later release.",
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
    mei,
    mei_research,
    outlier,
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

    Note that the files have to be linked with the case,
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

    institute_id = case_obj["owner"]
    institute_obj = adapter.institute(institute_id)
    if not institute_obj:
        LOG.info("Institute %s does not exist", institute_id)
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
        {"category": "mei", "variant_type": "clinical", "upload": mei},
        {"category": "mei", "variant_type": "research", "upload": mei_research},
        {"category": "sv", "variant_type": "clinical", "upload": sv},
        {"category": "sv", "variant_type": "research", "upload": sv_research},
        {"category": "snv", "variant_type": "clinical", "upload": snv},
        {"category": "snv", "variant_type": "research", "upload": snv_research},
        {"category": "str", "variant_type": "clinical", "upload": str_clinical},
    ]

    omics_files = [
        {
            "category": "outlier",
            "variant_type": "clinical",
            "upload": outlier,
        },
    ]

    gene_obj = None
    if hgnc_id or hgnc_symbol:
        if hgnc_id:
            gene_obj = adapter.hgnc_gene(hgnc_id, case_obj["genome_build"])
        if hgnc_symbol:
            for res in adapter.gene_aliases(hgnc_symbol, case_obj["genome_build"]):
                gene_obj = res
        if not gene_obj:
            LOG.warning("The gene could not be found")
            raise click.Abort()

    old_sanger_variants = adapter.case_sanger_variants(case_obj["_id"])
    old_evaluated_variants = None  # acmg, manual rank, cancer tier, dismissed, mosaic, commented

    if keep_actions:  # collect all variants with user actions for this case
        old_evaluated_variants = list(adapter.evaluated_variants(case_id, institute_id))

    def load_variant_files(
        case_obj: dict, files: List[Dict], rank_threshold: int, force: bool
    ) -> int:
        """Load variants from indicated VCF files. Keep count of files used for logging blank commands."""
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

            LOG.info(
                "Delete {0} {1} variants for case {2}".format(
                    variant_type, category, case_obj["_id"]
                )
            )

            adapter.delete_variants(
                case_id=case_obj["_id"], variant_type=variant_type, category=category
            )

            LOG.info(
                "Load {0} {1} variants for case {2}".format(variant_type, category, case_obj["_id"])
            )

            try:
                adapter.load_variants(
                    case_obj=case_obj,
                    variant_type=variant_type,
                    category=category,
                    rank_threshold=rank_threshold,
                    chrom=chrom,
                    start=start,
                    end=end,
                    gene_obj=gene_obj,
                    build=case_obj["genome_build"],
                )
                # Update case variants count
                adapter.case_variants_count(case_obj["_id"], institute_id, force_update_case=True)

            except Exception as e:
                LOG.warning(e)
                raise click.Abort()

        return i

    def load_omics_variant_files(case_obj: dict, omics_files: List[Dict]) -> int:
        """Load variants from indicated VCF files. Keep count of files used for logging blank commands."""
        i = 0
        for file_type in omics_files:
            variant_type = file_type["variant_type"]
            category = file_type["category"]

            if not file_type["upload"]:
                continue

            i += 1
            LOG.info(
                "Delete {0} {1} OMICS variants for case {2}".format(
                    variant_type, category, case_obj["_id"]
                )
            )

            adapter.delete_omics_variants_by_category(
                case_id=case_obj["_id"], variant_type=variant_type, category=category
            )

            for file_type, omics_file_type in OMICS_FILE_TYPE_MAP.items():
                if (
                    omics_file_type["variant_type"] != variant_type
                    or omics_file_type["category"] != category
                ):
                    continue

                i += 1
                LOG.info(
                    "Load {0} {1} variants for case {2}".format(
                        variant_type, category, case_obj["_id"]
                    )
                )

                build = case_obj.get("rna_genome_build", case_obj.get("genome_build", "38"))

                try:
                    adapter.load_omics_variants(
                        case_obj=case_obj,
                        file_type=file_type,
                        build=build,
                    )
                    # Update case variants count
                    adapter.case_variants_count(
                        case_obj["_id"], institute_id, force_update_case=True
                    )

                except Exception as e:
                    LOG.warning(e)
                    raise click.Abort()

        return i

    i = load_variant_files(case_obj, files, rank_treshold, force)
    i += load_omics_variant_files(
        case_obj,
        omics_files,
    )

    if i == 0:
        LOG.info("No files where specified to upload variants from")

    # update Sanger status for the new inserted variants
    adapter.update_case_sanger_variants(institute_obj, case_obj, old_sanger_variants)

    if keep_actions and old_evaluated_variants:
        adapter.update_variant_actions(institute_obj, case_obj, old_evaluated_variants)
