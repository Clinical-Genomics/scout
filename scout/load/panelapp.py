import logging
import math
from datetime import datetime
from typing import Dict, List, Set

from click import Abort, progressbar

from scout.adapter import MongoAdapter
from scout.constants.panels import PRESELECTED_PANELAPP_PANEL_TYPE_SLUGS
from scout.parse.panelapp import parse_panelapp_panel
from scout.server.extensions import panelapp

LOG = logging.getLogger(__name__)
PANEL_NAME = "PANELAPP-GREEN"


def load_panelapp_panel(
    adapter: MongoAdapter,
    panel_id: str = None,
    institute: str = "cust000",
    confidence: str = "green",
):
    """Load PanelApp panels into scout database."""

    panel_ids = [panel_id]

    if not panel_id:
        LOG.info("Fetching all panel app panels")
        panel_ids: List[str] = panelapp.get_panel_ids(signed_off=False)

    ensembl_id_to_hgnc_id_map: Dict[str, int] = adapter.ensembl_to_hgnc_id_mapping()
    hgnc_symbol_to_ensembl_id_map: Dict[int, str] = adapter.hgnc_symbol_ensembl_id_mapping()

    for _ in panel_ids:
        panel_info: dict = panelapp.get_panel(panel_id)
        parsed_panel = parse_panelapp_panel(
            panel_info=panel_info,
            ensembl_id_to_hgnc_id_map=ensembl_id_to_hgnc_id_map,
            hgnc_symbol_to_ensembl_id_map=hgnc_symbol_to_ensembl_id_map,
            institute=institute,
            confidence=confidence,
        )

        if len(parsed_panel["genes"]) == 0:
            LOG.warning("Panel %s is missing genes. Skipping.", parsed_panel["display_name"])
            continue

        adapter.load_panel(parsed_panel=parsed_panel, replace=True)


def get_panelapp_genes(
    adapter: MongoAdapter, institute: str, panel_ids: List[str], types_filter: List[str]
) -> Set[tuple]:
    """Parse and collect genes from one or more panelApp panels."""

    genes = set()
    ensembl_id_to_hgnc_id_map: Dict[str, int] = adapter.ensembl_to_hgnc_id_mapping()
    hgnc_symbol_to_ensembl_id_map: Dict[int, str] = adapter.hgnc_symbol_ensembl_id_mapping()

    with progressbar(panel_ids, label="Parsing panels", length=len(panel_ids)) as panel_ids:
        for panel_id in panel_ids:
            panel_dict: dict = panelapp.get_panel(panel_id)
            panel_type_slugs = [type["slug"] for type in panel_dict.get("types")]
            # Parse panel only if it's of the expect type(s)
            if not set(types_filter).intersection(panel_type_slugs):
                continue

            parsed_panel = parse_panelapp_panel(
                panel_info=panel_dict,
                ensembl_id_to_hgnc_id_map=ensembl_id_to_hgnc_id_map,
                hgnc_symbol_to_ensembl_id_map=hgnc_symbol_to_ensembl_id_map,
                institute=institute,
                confidence="green",
            )
            genes.update(
                {(gene["hgnc_id"], gene["hgnc_symbol"]) for gene in parsed_panel.get("genes")}
            )

    return genes


def load_panelapp_green_panel(adapter: MongoAdapter, institute: str, force: bool, signed_off: bool):
    """Load/Update the panel containing all Panelapp Green genes."""

    def parse_types_filter(types_filter: str, available_types: List[str]) -> List[str]:
        """Translate panel type input from users to panel type slugs."""
        if not types_filter:
            return PRESELECTED_PANELAPP_PANEL_TYPE_SLUGS
        index_list = [int(typeint) - 1 for typeint in types_filter.replace(" ", "").split(",")]
        return [available_types[i] for i in index_list]

    # check and set panel version
    old_panel = adapter.gene_panel(panel_id=PANEL_NAME)
    green_panel = {
        "panel_name": PANEL_NAME,
        "display_name": "PanelApp Green Genes",
        "institute": institute,
        "version": float(math.floor(old_panel["version"]) + 1) if old_panel else 1.0,
        "date": datetime.now(),
    }

    LOG.info("Fetching all PanelApp panels")

    panel_ids = panelapp.get_panel_ids(signed_off=signed_off)
    LOG.info(f"\n\nQuery returned {len(panel_ids)} panels\n")
    LOG.info("Panels have the following associated types:")
    available_types: List[str] = panelapp.get_panel_types()
    for number, type in enumerate(available_types, 1):
        LOG.info(f"{number}: {type}")
    preselected_options_idx: List[str] = [
        str(available_types.index(presel) + 1)
        for presel in PRESELECTED_PANELAPP_PANEL_TYPE_SLUGS
        if presel in available_types
    ]
    types_filter: str = input(
        f"Please provide a comma-separated list of types you'd like to use to build your panel (leave blank to use the following types:{', '.join(preselected_options_idx)}):  "
    )
    types_filter: List[str] = parse_types_filter(
        types_filter=types_filter, available_types=available_types
    )
    LOG.info(f"Collecting green genes from panels of type: {types_filter}")
    green_panel["description"] = (
        f"This panel contains green genes from {'signed off ' if signed_off else ''}panels of the following types: {', '.join(types_filter)}"
    )
    genes: Set[tuple] = get_panelapp_genes(
        adapter=adapter, institute=institute, panel_ids=panel_ids, types_filter=types_filter
    )
    green_panel["genes"] = [{"hgnc_id": tup[0], "hgnc_symbol": tup[1]} for tup in genes]

    # Do not update panel if new version contains less genes and force flag is False
    if old_panel and len(old_panel.get("genes")) > len(green_panel["genes"]):
        LOG.warning(
            f"This new version of PANELAPP-GREEN contains less genes (n={len(green_panel['genes'])}) than the previous one (n={len(old_panel['genes'])})"
        )
        if force is False:
            LOG.error("Aborting. Please use the force flag -f to update the panel anyway")
            return
    adapter.load_panel(parsed_panel=green_panel, replace=True)
