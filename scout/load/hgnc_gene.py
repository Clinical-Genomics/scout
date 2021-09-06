# -*- coding: utf-8 -*-
import logging

from pprint import pprint as pp

from click import progressbar

from scout.build import build_hgnc_gene
from scout.utils.link import link_genes

from scout.utils.scout_requests import (
    fetch_ensembl_genes,
    fetch_hgnc,
    fetch_mim_files,
    fetch_exac_constraint,
    fetch_hpo_files,
    fetch_ensembl_transcripts,
    fetch_ensembl_exons,
)

from scout.load.transcript import load_transcripts

LOG = logging.getLogger(__name__)


def load_hgnc(
    adapter,
    genes=None,
    ensembl_lines=None,
    hgnc_lines=None,
    exac_lines=None,
    mim2gene_lines=None,
    genemap_lines=None,
    hpo_lines=None,
    transcripts_lines=None,
    build="37",
    omim_api_key="",
):
    """Load Genes and transcripts into the database

    If no resources are provided the correct ones will be fetched.

    Args:
        adapter(scout.adapter.MongoAdapter)
        genes(dict): If genes are already parsed
        ensembl_lines(iterable(str)): Lines formated with ensembl gene information
        hgnc_lines(iterable(str)): Lines with gene information from genenames.org
        exac_lines(iterable(str)): Lines with information pLi-scores from ExAC
        mim2gene(iterable(str)): Lines with map from omim id to gene symbol
        genemap_lines(iterable(str)): Lines with information of omim entries
        hpo_lines(iterable(str)): Lines information about map from hpo terms to genes
        transcripts_lines(iterable): iterable with ensembl transcript lines
        build(str): What build to use. Defaults to '37'

    """
    gene_objs = load_hgnc_genes(
        adapter=adapter,
        genes=genes,
        ensembl_lines=ensembl_lines,
        hgnc_lines=hgnc_lines,
        exac_lines=exac_lines,
        mim2gene_lines=mim2gene_lines,
        genemap_lines=genemap_lines,
        hpo_lines=hpo_lines,
        build=build,
        omim_api_key=omim_api_key,
    )

    ensembl_genes = {}
    for gene_obj in gene_objs:
        ensembl_genes[gene_obj["ensembl_id"]] = gene_obj

    transcript_objs = load_transcripts(
        adapter=adapter,
        transcripts_lines=transcripts_lines,
        build=build,
        ensembl_genes=ensembl_genes,
    )


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
        ensembl_lines(iterable(str)): Lines formated with ensembl gene information
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
            ensembl_lines = fetch_ensembl_genes(build=build)
        hgnc_lines = hgnc_lines or fetch_hgnc()
        exac_lines = exac_lines or fetch_exac_constraint()
        if not (mim2gene_lines and genemap_lines):
            if not omim_api_key:
                LOG.warning("No omim api key provided!")
            else:
                mim_files = fetch_mim_files(omim_api_key, mim2genes=True, genemap2=True)
                mim2gene_lines = mim_files["mim2genes"]
                genemap_lines = mim_files["genemap2"]
        if not hpo_lines:
            hpo_files = fetch_hpo_files(hpogenes=True)
            hpo_lines = hpo_files["hpogenes"]

        # Link the resources
        genes = link_genes(
            ensembl_lines=ensembl_lines,
            hgnc_lines=hgnc_lines,
            exac_lines=exac_lines,
            hpo_lines=hpo_lines,
            mim2gene_lines=mim2gene_lines,
            genemap_lines=genemap_lines,
        )

    non_existing = 0
    nr_genes = len(genes)

    with progressbar(genes.values(), label="Building genes", length=nr_genes) as bar:
        for gene_data in bar:
            if not gene_data.get("chromosome"):
                LOG.debug(
                    "skipping gene: %s. No coordinates found",
                    gene_data.get("hgnc_symbol", "?"),
                )
                non_existing += 1
                continue

            gene_obj = build_hgnc_gene(gene_data, build=build)
            gene_objects.append(gene_obj)

    LOG.info("Loading genes build %s", build)
    adapter.load_hgnc_bulk(gene_objects)

    LOG.info("Loading done. %s genes loaded", len(gene_objects))
    LOG.info("Nr of genes without coordinates in build %s: %s", build, non_existing)

    return gene_objects
