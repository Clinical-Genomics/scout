# -*- coding: utf-8 -*-
import logging

from scout.constants import FILE_TYPE_MAP
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
        gene_caption = adapter.hgnc_gene_caption(hgnc_id, case_obj["genome_build"])
        if not gene_caption:
            ValueError("Gene {} does not exist in database".format(hgnc_id))
        chrom = gene_caption["chromosome"]
        start = gene_caption["start"]
        end = gene_caption["end"]

    case_file_types = []

    for file_type in FILE_TYPE_MAP:
        if case_obj.get("vcf_files", {}).get(file_type):
            case_file_types.append(
                (FILE_TYPE_MAP[file_type]["variant_type"], FILE_TYPE_MAP[file_type]["category"])
            )

    for variant_type, category in case_file_types:
        if variant_type == "research" and not case_obj["is_research"]:
            continue

        LOG.info(
            "Load {} {} variants for case: {} region: chr {}, start {}, end {}".format(
                category, variant_type.upper(), case_obj["_id"], chrom, start, end
            )
        )
        adapter.load_variants(
            case_obj=case_obj,
            variant_type=variant_type,
            category=category,
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

    DEPRECATED method, historically used by the CG monolith, which has since switched to call the Scout CLI instead.
    """
    LOG.warning("Deprecated method. Be advised it will no longer available in Scout v5.")

    LOG.info("Check that the panels exists")
    if not check_panels(adapter, config.get("gene_panels", []), config.get("default_gene_panels")):
        raise ConfigError("Some panel(s) does not exist in the database")
    case_obj = adapter.load_case(config, update=update)
    return case_obj
