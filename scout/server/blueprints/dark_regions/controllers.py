import logging

from scout.constants import GENOME_REGION, INHERITANCE_PALETTE
from scout.server.blueprints.cases.controllers import _get_events, _populate_case_individuals
from scout.server.blueprints.dark_regions.helpers import SMN_HGNC_IDS, _get_paraphrase_regions
from scout.server.utils import case_has_alignments, get_case_genome_build

LOG = logging.getLogger(__name__)


def sma_case(store, institute_obj, case_obj, selected_gene_panels=None):
    """Preprocess a case for the dark regions SMA view."""

    _populate_case_individuals(case_obj)
    case_has_alignments(case_obj)

    selected_gene_panels = selected_gene_panels or []
    panel_hgnc_ids = {
        hgnc_id
        for hgnc_id in store.panels_to_genes(
            panel_names=selected_gene_panels, gene_format="hgnc_id"
        )
        if isinstance(hgnc_id, int)
    }
    if "hpo" in selected_gene_panels:
        panel_hgnc_ids.update(
            gene.get("hgnc_id")
            for gene in case_obj.get("dynamic_gene_list", [])
            if isinstance(gene.get("hgnc_id"), int)
        )

    show_smn_section = (not selected_gene_panels) or bool(SMN_HGNC_IDS.intersection(panel_hgnc_ids))

    return {
        "institute": institute_obj,
        "case": case_obj,
        "comments": store.events(institute_obj, case=case_obj, comments=True),
        "events": _get_events(store, institute_obj, case_obj),
        "region": GENOME_REGION[get_case_genome_build(case_obj)],
        "paraphrase_regions": _get_paraphrase_regions(case_obj, panel_hgnc_ids),
        "inherit_palette": INHERITANCE_PALETTE,
        "selected_gene_panels": selected_gene_panels,
        "show_smn_section": show_smn_section,
    }
