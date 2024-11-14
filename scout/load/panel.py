"""scout.load.panel.py

functions to load panels into the database

"""

import logging
import math
from datetime import datetime
from typing import Dict, List, Set

from click import Abort, progressbar
from flask.cli import current_app

from scout.adapter import MongoAdapter
from scout.parse.panel import get_panel_info, parse_gene_panel, parse_panel_app_panel
from scout.server.extensions import panelapp
from scout.utils.handle import get_file_handle
from scout.utils.scout_requests import fetch_mim_files

LOG = logging.getLogger(__name__)
PANEL_NAME = "PANELAPP-GREEN"


def load_panel(panel_path, adapter, **kwargs):
    """Load a manually curated gene panel into scout

    Args:
        panel_path(str): path to gene panel file
        adapter(scout.adapter.MongoAdapter)
        date(str): date of gene panel on format 2017-12-24
        display_name(str)
        version(float)
        panel_type(str)
        panel_id(str)
        institute(str)
        maintainer(str)

    """
    panel_lines = get_file_handle(panel_path)
    version = kwargs.get("version")

    try:
        # This will parse panel metadata if includeed in panel file
        panel_info = get_panel_info(
            panel_lines=panel_lines,
            panel_id=kwargs.get("panel_id"),
            institute=kwargs.get("institute"),
            version=version,
            date=kwargs.get("date"),
            maintatiner=kwargs.get("maintainer"),
            display_name=kwargs.get("display_name"),
        )
    except Exception as err:
        raise err

    if panel_info.get("version"):
        version = float(panel_info["version"])

    panel_id = panel_info["panel_id"]
    display_name = panel_info["display_name"] or panel_id
    institute = panel_info["institute"]
    date = panel_info["date"]

    if not institute:
        raise SyntaxError("A Panel has to belong to a institute")

    # Check if institute exists in database
    if not adapter.institute(institute):
        raise SyntaxError("Institute {0} does not exist in database".format(institute))

    if not panel_id:
        raise SyntaxError("A Panel has to have a panel id")

    if version:
        existing_panel = adapter.gene_panel(panel_id, version)
    else:
        # Assuming version 1.0
        existing_panel = adapter.gene_panel(panel_id)
        version = 1.0
        LOG.info("Set version to %s", version)

    if existing_panel:
        LOG.info("found existing panel")
        if version == existing_panel["version"]:
            LOG.warning("Panel with same version exists in database")
            LOG.info("Reload with updated version")
            raise SyntaxError()
        display_name = display_name or existing_panel["display_name"]
        institute = institute or existing_panel["institute"]

    # Check if maintainers exist in the user database
    maintainer = kwargs.get("maintainer")
    if maintainer is not None:
        if adapter.user(user_id=maintainer) is None:
            LOG.warning("Maintainer %s does not exist in user database", maintainer)
            raise Abort()

    try:
        parsed_panel = parse_gene_panel(
            path=panel_path,
            institute=institute,
            panel_type=kwargs.get("panel_type"),
            date=date,
            version=version,
            panel_id=panel_id,
            maintainer=maintainer,
            display_name=display_name,
        )
        adapter.load_panel(parsed_panel=parsed_panel)
    except Exception as err:
        raise err


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

            parsed_panel = parse_panel_app_panel(
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
        parsed_panel = parse_panel_app_panel(
            panel_info=panel_info,
            ensembl_id_to_hgnc_id_map=ensembl_id_to_hgnc_id_map,
            hgnc_symbol_to_ensembl_id_map=hgnc_symbol_to_ensembl_id_map,
            institute=institute,
            confidence=confidence,
        )

        if len(parsed_panel["genes"]) == 0:
            LOG.warning("Panel %s is missing genes. Skipping.", parsed_panel["display_name"])
            continue

        try:
            adapter.load_panel(parsed_panel=parsed_panel, replace=True)
        except Exception as err:
            raise err


def load_panelapp_green_panel(adapter: MongoAdapter, institute: str, force: bool, signed_off: bool):
    """Load/Update the panel containing all Panelapp Green genes."""

    def parse_types_filter(types_filter: str, available_types: List[str]) -> List[str]:
        """Translate panel type input from users to panel type slugs."""
        if not types_filter:
            return available_types
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
    types_filter: str = input(
        "Please provide a comma-separated list of types you'd like to use to build your panel (leave blank to use all types):  "
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
    if old_panel and len(old_panel.get("genes", [])) > len(green_panel["genes"]):
        LOG.warning(
            f"This new version of PANELAPP-GREEN contains less genes (n={len(green_panel['genes'])}) than the previous one (n={len(old_panel['genes'])})"
        )
        if force is False:
            LOG.error("Aborting. Please use the force flag -f to update the panel anyway")
            return

    adapter.load_panel(parsed_panel=green_panel, replace=True)


def load_omim_panel(adapter, genemap2, mim2genes, api_key, institute):
    """Add OMIM panel to the database.
    Args:
        adapter(scout.adapter.MongoAdapter)
        genemap2(str): Path to file in omim genemap2 format
        mim2genes(str): Path to file in omim mim2genes format
        api_key(str): OMIM API key
        institute(str): institute _id
    """

    mim_files = None
    if genemap2 and mim2genes:
        mim_files = {
            "genemap2": list(get_file_handle(genemap2)),
            "mim2genes": list(get_file_handle(mim2genes)),
        }

    api_key = api_key or current_app.config.get("OMIM_API_KEY")
    if not api_key and mim_files is None:
        LOG.warning(
            "Please provide either an OMIM api key or the path to genemap2 and mim2genesto to load the omim gene panel"
        )
        return
    # Check if OMIM-AUTO exists
    if adapter.gene_panel(panel_id="OMIM-AUTO"):
        LOG.warning(
            "OMIM-AUTO already exists in database. Use the command 'scout update omim' to create a new OMIM panel version"
        )
        return

    if not mim_files:
        mim_files = fetch_mim_files(api_key=api_key, genemap2=True, mim2genes=True)

    # Here we know that there is no panel loaded
    try:
        adapter.load_omim_panel(
            genemap2_lines=mim_files["genemap2"],
            mim2gene_lines=mim_files["mim2genes"],
            institute=institute,
        )
    except Exception as err:
        LOG.error(err)
