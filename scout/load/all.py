# -*- coding: utf-8 -*-
import logging

from scout.exceptions.config import ConfigError

LOG = logging.getLogger(__name__)


def check_panels(adapter, panels, default_panels=None):
    """Make sure that the gene panels exist in the database
    Also check if the default panels are defined in gene panels

    Args:
        adapter(MongoAdapter)
        panels(list(str)): A list with panel names

    Returns:
        panels_exists(bool)
    """
    default_panels = default_panels or []
    panels_exist = True
    for panel in default_panels:
        if panel not in panels:
            LOG.warning("Default panels have to be defined in panels")
            panels_exist = False
    for panel in panels:
        if not adapter.gene_panel(panel):
            LOG.warning("Panel {} does not exist in database".format(panel))
            panels_exist = False
    return panels_exist


def load_region(adapter, case_id, hgnc_id=None, chrom=None, start=None, end=None):
    """Load all variants in a region defined by a HGNC id

    Args:
        adapter (MongoAdapter)
        case_id (str): Case id
        hgnc_id (int): If all variants from a gene should be uploaded
        chrom (str): If variants from coordinates should be uploaded
        start (int): Start position for region
        end (int): Stop position for region
    """
    case_obj = adapter.case(case_id=case_id)
    if not case_obj:
        raise ValueError("Case {} does not exist in database".format(case_id))

    if hgnc_id:
        gene_obj = adapter.hgnc_gene(hgnc_id, case_obj["genome_build"])
        if not gene_obj:
            ValueError("Gene {} does not exist in database".format(hgnc_id))
        chrom = gene_obj["chromosome"]
        start = gene_obj["start"]
        end = gene_obj["end"]

    LOG.info(
        "Load clinical SNV variants for case: {0} region: chr {1}, start"
        " {2}, end {3}".format(case_obj["_id"], chrom, start, end)
    )

    adapter.load_variants(
        case_obj=case_obj,
        variant_type="clinical",
        category="snv",
        chrom=chrom,
        start=start,
        end=end,
    )

    # loading germline variants
    vcf_sv_file = case_obj["vcf_files"].get("vcf_sv")
    if vcf_sv_file:
        LOG.info(
            "Load clinical SV variants for case: {0} region: chr {1}, "
            "start {2}, end {3}".format(case_obj["_id"], chrom, start, end)
        )
        adapter.load_variants(
            case_obj=case_obj,
            variant_type="clinical",
            category="sv",
            chrom=chrom,
            start=start,
            end=end,
        )

    # if there are somatic (cancer) variants:
    vcf_cancer_sv_file = case_obj["vcf_files"].get("vcf_cancer_sv")
    if vcf_cancer_sv_file:
        LOG.info(
            "Load clinical cancer SV variants for case: {0} region: chr {1}, "
            "start {2}, end {3}".format(case_obj["_id"], chrom, start, end)
        )
        adapter.load_variants(
            case_obj=case_obj,
            variant_type="clinical",
            category="cancer_sv",
            chrom=chrom,
            start=start,
            end=end,
        )

    vcf_str_file = case_obj["vcf_files"].get("vcf_str")
    if vcf_str_file:
        LOG.info("Load all clinical STR variants for case: {0}.")
        adapter.load_variants(case_obj=case_obj, variant_type="clinical", category="str")

    if case_obj["is_research"]:
        LOG.info(
            "Load research SNV variants for case: {0} region: chr {1}, "
            "start {2}, end {3}".format(case_obj["_id"], chrom, start, end)
        )
        adapter.load_variants(
            case_obj=case_obj,
            variant_type="research",
            category="snv",
            chrom=chrom,
            start=start,
            end=end,
        )

        vcf_sv_research = case_obj["vcf_files"].get("vcf_sv_research")
        if vcf_sv_research:
            LOG.info(
                "Load research SV variants for case: {0} region: chr {1},"
                " start {2}, end {3}".format(case_obj["_id"], chrom, start, end)
            )
            adapter.load_variants(
                case_obj=case_obj,
                variant_type="research",
                category="sv",
                chrom=chrom,
                start=start,
                end=end,
            )
    # Update case variants count
    adapter.case_variants_count(case_obj["_id"], case_obj["owner"], force_update_case=True)


def load_scout(adapter, config, ped=None, update=False):
    """Load a new case from a Scout config.

    Args:
        adapter(MongoAdapter)
        config(dict): loading info
        ped(Iterable(str)): Pedigree ingformation
        update(bool): If existing case should be updated

    """
    LOG.info("Check that the panels exists")
    if not check_panels(adapter, config.get("gene_panels", []), config.get("default_gene_panels")):
        raise ConfigError("Some panel(s) does not exist in the database")
    case_obj = adapter.load_case(config, update=update)
    return case_obj
