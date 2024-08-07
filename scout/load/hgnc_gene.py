# -*- coding: utf-8 -*-
import logging
from typing import Dict

from click import progressbar

from scout.build import build_hgnc_gene
from scout.utils.ensembl_biomart_clients import EnsemblBiomartHandler
from scout.utils.link import link_genes
from scout.utils.scout_requests import (
    fetch_constraint,
    fetch_hgnc,
    fetch_hpo_files,
    fetch_mim_files,
)

LOG = logging.getLogger(__name__)


def set_missing_gene_coordinates(gene_data: dict, cytoband_coords: Dict[str, dict]):
    """Attempt at collecting gene coordinates from cytoband for genes missing Ensembl ID."""

    if gene_data.get("ensembl_gene_id") not in [
        "",
        None,
    ]:  # Coordinates are present, since they're collected from the Ensembl file
        return
    gene_data["ensembl_gene_id"] = None
    cytoband_coord: dict = cytoband_coords.get(gene_data["location"])
    if cytoband_coord:
        gene_data["chromosome"]: str = cytoband_coord["chromosome"]
        gene_data["start"]: int = cytoband_coord["start"]
        gene_data["end"]: int = cytoband_coord["stop"]


def load_hgnc_genes(
    adapter,
    genes=None,
    ensembl_lines=None,
    hgnc_lines=None,
    exac_lines=None,
    mim2gene_lines=None,
    genemap_lines=None,
    hpo_lines=None,
    build="37",
    omim_api_key="",
):
    """Load genes into the database

    link_genes will collect information from all the different sources and
    merge it into a dictionary with hgnc_id as key and gene information as values.

    Args:
        adapter(scout.adapter.MongoAdapter)
        genes(dict): If genes are already parsed
        ensembl_lines(iterable(str)): Lines formatted with ensembl gene information
        hgnc_lines(iterable(str)): Lines with gene information from genenames.org
        exac_lines(iterable(str)): Lines with information pLi-scores from ExAC
        mim2gene(iterable(str)): Lines with map from omim id to gene symbol
        genemap_lines(iterable(str)): Lines with information of omim entries
        hpo_lines(iterable(str)): Lines information about map from hpo terms to genes
        build(str): What build to use. Defaults to '37'

    Returns:
        gene_objects(list): A list with all gene_objects that was loaded into database
    """
    gene_objects = list()

    if not genes:
        # Fetch the resources if not provided
        if ensembl_lines is None:
            ensembl_client = EnsemblBiomartHandler(build=build)
            ensembl_lines = ensembl_client.stream_resource(interval_type="genes")
        hgnc_lines = hgnc_lines or fetch_hgnc()
        exac_lines = exac_lines or fetch_constraint()
        if not (mim2gene_lines and genemap_lines):
            if not omim_api_key:
                LOG.warning("No omim api key provided!")
            else:
                mim_files = fetch_mim_files(omim_api_key, mim2genes=True, genemap2=True)
                mim2gene_lines = mim_files["mim2genes"]
                genemap_lines = mim_files["genemap2"]

        if not hpo_lines:
            hpo_files = fetch_hpo_files(genes_to_phenotype=True)
            hpo_lines = hpo_files["genes_to_phenotype"]

        # Link the resources
        genes = link_genes(
            ensembl_lines=ensembl_lines,
            hgnc_lines=hgnc_lines,
            exac_lines=exac_lines,
            hpo_lines=hpo_lines,
            mim2gene_lines=mim2gene_lines,
            genemap_lines=genemap_lines,
        )

    without_coords = 0
    nr_genes = len(genes)
    LOG.info(f"Building info for {nr_genes} genes")

    cytoband_coords: Dict[str, dict] = adapter.cytoband_to_coordinates(build=build)

    with progressbar(genes.values(), label="Building genes", length=nr_genes) as bar:
        for gene_data in bar:
            set_missing_gene_coordinates(gene_data=gene_data, cytoband_coords=cytoband_coords)

            if not gene_data.get("chromosome"):
                without_coords += 1
                continue
            gene_obj = build_hgnc_gene(
                gene_data,
                build=build,
            )

            if gene_obj:
                gene_objects.append(gene_obj)
            else:
                without_coords += 1

    LOG.info(
        "Nr of genes without coordinates in build %s and therefore skipped: %s",
        build,
        without_coords,
    )
    LOG.info(f"Loading {len(gene_objects)} genes into the database")

    adapter.load_hgnc_bulk(gene_objects)

    LOG.info("Loading done. %s genes loaded", len(gene_objects))

    return gene_objects
