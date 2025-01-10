"""Code to parse panel information"""

import logging
from typing import Dict, Optional

from scout.constants import INCOMPLETE_PENETRANCE_MAP, MODELS_MAP, PANELAPP_CONFIDENCE_EXCLUDE
from scout.utils.date import get_date

LOG = logging.getLogger(__name__)
PANELAPP_PANELS_URL = "https://panelapp.genomicsengland.co.uk/panels/"


def parse_panel_app_gene(
    panelapp_gene: dict,
    confidence: str,
) -> dict:
    """Parse a panel app-formatted gene."""
    gene_info = {}
    confidence_level = panelapp_gene["confidence_level"]
    # Return empty gene if not confident gene
    if confidence_level in PANELAPP_CONFIDENCE_EXCLUDE[confidence]:
        return gene_info

    gene_info["hgnc_symbol"] = panelapp_gene["gene_data"]["gene_symbol"]
    gene_info["hgnc_id"] = panelapp_gene["gene_data"]["hgnc_id"].split(":")[1]
    gene_info["reduced_penetrance"] = INCOMPLETE_PENETRANCE_MAP.get(panelapp_gene["penetrance"])

    inheritance_models = []
    for model in MODELS_MAP.get(panelapp_gene["mode_of_inheritance"], []):
        inheritance_models.append(model)

    gene_info["inheritance_models"] = inheritance_models

    return gene_info


def parse_panelapp_panel(
    panel_info: dict,
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
    gene_panel["description"] = f"{PANELAPP_PANELS_URL}{panel_id}"

    LOG.info("Parsing panel %s", gene_panel["display_name"])

    gene_panel["genes"] = []

    nr_excluded = 0
    nr_genes = 0
    for nr_genes, gene in enumerate(panel_info["genes"], 1):
        gene_info = parse_panel_app_gene(gene, confidence)
        if not gene_info:
            nr_excluded += 1
            continue
        gene_panel["genes"].append(gene_info)

    LOG.info("Number of genes in panel %s", nr_genes)
    LOG.info("Number of genes excluded due to confidence threshold: %s", nr_excluded)

    return gene_panel
