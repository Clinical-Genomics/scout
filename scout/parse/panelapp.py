"""Code to parse panel information"""

import logging
from typing import Dict, List, Optional

from scout.constants import INCOMPLETE_PENETRANCE_MAP, MODELS_MAP, PANELAPP_CONFIDENCE_EXCLUDE
from scout.utils.date import get_date

LOG = logging.getLogger(__name__)


def parse_panel_app_gene(
    panelapp_gene: dict,
    ensembl_gene_hgnc_id_map: Dict[str, int],
    hgnc_symbol_ensembl_gene_map: Dict[str, str],
    confidence: str,
) -> dict:
    """Parse a panel app-formatted gene."""
    gene_info = {}
    confidence_level = panelapp_gene["confidence_level"]
    # Return empty gene if not confident gene
    if confidence_level in PANELAPP_CONFIDENCE_EXCLUDE[confidence]:
        return gene_info

    hgnc_symbol = panelapp_gene["gene_data"]["gene_symbol"]
    ensembl_ids = [
        version["ensembl_id"]
        for genome in panelapp_gene["gene_data"]["ensembl_genes"].values()
        for version in genome.values()
    ]

    if not ensembl_ids:  # This gene is probably tagged as ensembl_ids_known_missing on PanelApp
        if hgnc_symbol in hgnc_symbol_ensembl_gene_map:
            LOG.warning(
                f"PanelApp gene {hgnc_symbol} does not contain Ensembl IDs. Using Ensembl IDs from internal gene collection instead."
            )
            ensembl_ids = [hgnc_symbol_ensembl_gene_map[hgnc_symbol]]
        else:
            LOG.warning(
                f"PanelApp gene {hgnc_symbol} does not contain Ensembl IDs and gene symbol does not correspond to a gene in scout."
            )

    hgnc_ids = set(
        ensembl_gene_hgnc_id_map.get(ensembl_id)
        for ensembl_id in ensembl_ids
        if ensembl_gene_hgnc_id_map.get(ensembl_id)
    )
    if not hgnc_ids:
        LOG.warning("Gene %s does not exist in database. Skipping gene...", hgnc_symbol)
        return gene_info

    if len(hgnc_ids) > 1:
        LOG.warning("Gene %s has unclear identifier. Choose random id", hgnc_symbol)

    gene_info["hgnc_symbol"] = hgnc_symbol
    for hgnc_id in hgnc_ids:
        gene_info["hgnc_id"] = hgnc_id

    gene_info["reduced_penetrance"] = INCOMPLETE_PENETRANCE_MAP.get(panelapp_gene["penetrance"])

    inheritance_models = []
    for model in MODELS_MAP.get(panelapp_gene["mode_of_inheritance"], []):
        inheritance_models.append(model)

    gene_info["inheritance_models"] = inheritance_models

    return gene_info


def parse_panelapp_panel(
    panel_info: dict,
    ensembl_id_to_hgnc_id_map: Dict[str, int],
    hgnc_symbol_to_ensembl_id_map: Dict[str, str],
    institute: Optional[str] = "cust000",
    confidence: Optional[str] = "green",
) -> dict:
    """Parse a PanelApp panel"""

    date_format = "%Y-%m-%dT%H:%M:%S.%f"

    gene_panel = {}
    panel_id = str(panel_info["id"])
    if confidence != "green":
        gene_panel["panel_id"] = "_".join([panel_id, confidence])
    else:  # This way the old green panels will be overwritten, instead of creating 2 sets of green panels, old and new
        gene_panel["panel_id"] = panel_id

    gene_panel["version"] = float(panel_info["version"])
    gene_panel["date"] = get_date(panel_info["version_created"][:-1], date_format=date_format)
    gene_panel["display_name"] = " - ".join([panel_info["name"], f"[{confidence.upper()}]"])
    gene_panel["institute"] = institute
    gene_panel["panel_type"] = ("clinical",)

    LOG.info("Parsing panel %s", gene_panel["display_name"])

    gene_panel["genes"] = []

    nr_excluded = 0
    nr_genes = 0
    for nr_genes, gene in enumerate(panel_info["genes"], 1):
        gene_info = parse_panel_app_gene(
            gene, ensembl_id_to_hgnc_id_map, hgnc_symbol_to_ensembl_id_map, confidence
        )
        if not gene_info:
            nr_excluded += 1
            continue
        gene_panel["genes"].append(gene_info)

    LOG.info("Number of genes in panel %s", nr_genes)
    LOG.info("Number of genes excluded due to confidence threshold: %s", nr_excluded)

    return gene_panel
