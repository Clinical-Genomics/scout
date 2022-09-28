"""scout.load.panel.py

functions to load panels into the database

"""

import logging

from click import Abort
from flask.cli import current_app

from scout.parse.panel import get_panel_info, parse_gene_panel, parse_panel_app_panel
from scout.utils.handle import get_file_handle
from scout.utils.scout_requests import fetch_mim_files, fetch_resource

LOG = logging.getLogger(__name__)


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


def load_panelapp_panel(adapter, panel_id=None, institute="cust000", confidence="green"):
    """Load PanelApp panels into scout database

    If no panel_id load all PanelApp panels

    Args:
        adapter(scout.adapter.MongoAdapter)
        panel_id(str): The panel app panel id
        confidence(str enum green|amber|red): traffic light-style PanelApp level of confidence
    """
    base_url = "https://panelapp.genomicsengland.co.uk/WebServices/{0}/"

    hgnc_map = adapter.ensembl_to_hgnc_mapping()

    panel_ids = [panel_id]

    if not panel_id:
        LOG.info("Fetching all panel app panels")
        json_lines = fetch_resource(base_url.format("list_panels"), json=True)

        panel_ids = [panel_info["Panel_Id"] for panel_info in json_lines["result"]]

    for _panel_id in panel_ids:
        json_lines = fetch_resource(base_url.format("get_panel") + _panel_id, json=True)
        parsed_panel = parse_panel_app_panel(
            panel_info=json_lines["result"],
            hgnc_map=hgnc_map,
            institute=institute,
            confidence=confidence,
        )
        if confidence != "green":
            parsed_panel["panel_id"] = "_".join([_panel_id, confidence])
        else:  # This way the old green panels will be overwritten, instead of creating 2 sets of green panels, old and new
            parsed_panel["panel_id"] = _panel_id

        if len(parsed_panel["genes"]) == 0:
            LOG.warning("Panel %s is missing genes. Skipping.", parsed_panel["display_name"])
            continue

        try:
            adapter.load_panel(parsed_panel=parsed_panel, replace=True)
        except Exception as err:
            raise err


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
