# -*- coding: utf-8 -*-
import logging

from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)


def build_gene(gene_info: dict, adapter) -> dict:
    """Build a panel_gene object."""

    symbol = gene_info.get("hgnc_symbol")
    hgnc_id = gene_info.get("hgnc_id")

    # Validate presence of hgnc_id
    if not hgnc_id:
        raise KeyError(f"Gene {symbol} is missing hgnc id. Panel genes must have hgnc_id.")

    # Try fetching gene information from either build "37" or "38"
    hgnc_gene = adapter.hgnc_gene_caption(
        hgnc_identifier=hgnc_id, build="37"
    ) or adapter.hgnc_gene_caption(hgnc_identifier=hgnc_id, build="38")

    if hgnc_gene is None:
        raise IntegrityError(f"hgnc_id {hgnc_id} is not in the gene database!")

    gene_obj = {"hgnc_id": hgnc_id, "symbol": hgnc_gene["hgnc_symbol"]}

    # Log warnings if symbols do not match
    if symbol != gene_obj["symbol"]:
        LOG.warning(f"Symbol in database does not match symbol in panel file for gene {hgnc_id}")
        LOG.warning(f"Using symbol {gene_obj['symbol']} for gene {hgnc_id} instead of {symbol}")

    # Add optional gene information
    gene_obj.update(
        {
            key: gene_info[key]
            for key in ["disease_associated_transcripts", "comment", "database_entry_version"]
            if key in gene_info
        }
    )

    # Add boolean flags
    gene_obj.update(
        {key: True for key in ["reduced_penetrance", "mosaicism"] if gene_info.get(key)}
    )

    # Handle inheritance models
    if "inheritance_models" in gene_info:
        gene_obj["inheritance_models"] = gene_info["inheritance_models"]

    if "custom_inheritance_models" in gene_info:
        gene_obj["custom_inheritance_models"] = [
            model for model in gene_info["custom_inheritance_models"]
        ]

    return gene_obj


def build_panel(panel_info, adapter):
    """Build a gene_panel object

        Args:
            panel_info(dict): A dictionary with panel information
            adapter (scout.adapter.MongoAdapter)

        Returns:
            panel_obj(dict)

    gene_panel = dict(
        panel_id = str, # required
        institute = str, # institute_id, required
        maintainer = list, # list of user._id
        version = float, # required
        date = datetime, # required
        display_name = str, # default is panel_name
        description = str # optional panel description
        genes = list, # list of panel genes, sorted on panel_gene['symbol']
    )

    """

    panel_name = panel_info.get("panel_id", panel_info.get("panel_name"))

    if panel_name:
        panel_name = panel_name.strip()
    else:
        raise KeyError("Panel has to have a id")

    panel_obj = dict(panel_name=panel_name)
    LOG.info("Building panel with name: {0}".format(panel_name))

    try:
        institute_id = panel_info["institute"]
    except KeyError as err:
        raise KeyError("Panel has to have a institute")

    # Check if institute exists in database
    if adapter.institute(institute_id) is None:
        raise IntegrityError("Institute %s could not be found" % institute_id)

    panel_obj["institute"] = panel_info["institute"]

    panel_obj["version"] = float(panel_info["version"])

    try:
        panel_obj["date"] = panel_info["date"]
    except KeyError as err:
        raise KeyError("Panel has to have a date")

    panel_obj["maintainer"] = panel_info.get("maintainer", [])
    panel_obj["display_name"] = panel_info.get("display_name", panel_obj["panel_name"])
    if panel_obj["display_name"]:
        panel_obj["display_name"] = panel_obj["display_name"].strip()
    panel_obj["description"] = panel_info.get("description")

    gene_objs = []
    errors = []
    for gene_info in panel_info.get("genes", []):
        try:
            gene_obj = build_gene(gene_info, adapter)
            gene_objs.append(gene_obj)
        except IntegrityError as err:
            LOG.warning(err)
            errors.append(f"{gene_info.get('hgnc_symbol')} ({gene_info.get('hgnc_id')})")
    if errors:
        raise IntegrityError(
            f"The following genes: {', '.join(errors)} were not found in Scout database."
        )

    panel_obj["genes"] = gene_objs

    return panel_obj
