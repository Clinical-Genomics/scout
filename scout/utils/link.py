import sys
import logging

from pprint import pprint as pp

from scout.parse.hgnc import parse_hgnc_genes
from scout.parse.ensembl import (
    parse_ensembl_transcripts,
    parse_ensembl_exons,
    parse_ensembl_genes,
)
from scout.parse.exac import parse_exac_genes
from scout.parse.hpo_terms import get_incomplete_penetrance_genes
from scout.parse.omim import get_mim_genes

LOG = logging.getLogger(__name__)


def genes_by_alias(hgnc_genes):
    """Return a dictionary with hgnc symbols as keys

    Value of the dictionaries are information about the hgnc ids for a symbol.
    If the symbol is primary for a gene then dict('true') will exist.
    A list of hgnc ids that the symbol points to is in ids.

    Args:
        hgnc_genes(dict): a dictionary with hgnc_id as key and gene info as value

    Returns:
        alias_genes(dict):
            {
                'hgnc_symbol':{
                    'true': int,
                    'ids': list(int)
                    }
            }
    """
    alias_genes = {}
    for hgnc_id in hgnc_genes:
        gene = hgnc_genes[hgnc_id]
        # This is the primary symbol:
        hgnc_symbol = gene["hgnc_symbol"]

        for alias in gene["previous_symbols"]:
            true_id = None
            if alias == hgnc_symbol:
                true_id = hgnc_id
            if alias in alias_genes:
                alias_genes[alias.upper()]["ids"].add(hgnc_id)
                if true_id:
                    alias_genes[alias.upper()]["true"] = hgnc_id
            else:
                alias_genes[alias.upper()] = {"true": true_id, "ids": set([hgnc_id])}

    return alias_genes


def add_ensembl_info(genes, ensembl_lines):
    """Add the coordinates from ensembl

    Args:
        genes(dict): Dictionary with all genes
        ensembl_lines(iteable): Iteable with raw ensembl info
    """

    LOG.info("Adding ensembl coordinates")
    # Parse and add the ensembl gene info
    ensembl_genes = parse_ensembl_genes(ensembl_lines)

    for ensembl_gene in ensembl_genes:
        if not "hgnc_id" in ensembl_gene:
            LOG.debug(
                "Ensembl gene %s is missing hgnc id. Skipping",
                ensembl_gene.get("ensembl_gene_id"),
            )
            continue
        gene_obj = genes.get(ensembl_gene["hgnc_id"])
        if not gene_obj:
            continue
        gene_obj["chromosome"] = ensembl_gene["chrom"]
        gene_obj["start"] = ensembl_gene["gene_start"]
        gene_obj["end"] = ensembl_gene["gene_end"]
        # ensembl ids can differ between builds. The ensembl gene ids from HGNC are only
        # true for build 38. So we add correct information from ensembl
        gene_obj["ensembl_gene_id"] = ensembl_gene["ensembl_gene_id"]


def add_exac_info(genes, alias_genes, exac_lines):
    """Add information from the exac genes

    Currently we only add the pLi score on gene level

    The exac resource only use HGNC symbol to identify genes so we need
    our alias mapping.

    Args:
        genes(dict): Dictionary with all genes
        alias_genes(dict): Genes mapped to all aliases
        ensembl_lines(iteable): Iteable with raw ensembl info

    """
    LOG.info("Add exac pli scores")
    for exac_gene in parse_exac_genes(exac_lines):
        hgnc_symbol = exac_gene["hgnc_symbol"].upper()
        pli_score = exac_gene["pli_score"]

        for hgnc_id in get_correct_ids(hgnc_symbol, alias_genes):
            genes[hgnc_id]["pli_score"] = pli_score


def add_omim_info(genes, alias_genes, genemap_lines, mim2gene_lines):
    """Add omim information

    We collect information on what phenotypes that are associated with a gene,
    what inheritance models that are associated and the correct omim id.

    Args:
        genes(dict): Dictionary with all genes
        alias_genes(dict): Genes mapped to all aliases
        genemap_lines(iterable): Iterable with raw omim info
        mim2gene_lines(iterable): Iterable with raw omim info

    """
    LOG.info("Add omim info")
    omim_genes = get_mim_genes(genemap_lines, mim2gene_lines)

    for hgnc_symbol in omim_genes:
        omim_info = omim_genes[hgnc_symbol]
        inheritance = omim_info.get("inheritance", set())

        for hgnc_id in get_correct_ids(hgnc_symbol, alias_genes):
            gene_info = genes[hgnc_id]

            # Update the omim id to the one found in omim
            gene_info["omim_id"] = omim_info["mim_number"]

            gene_info["inheritance_models"] = list(inheritance)
            gene_info["phenotypes"] = omim_info.get("phenotypes", [])


def add_incomplete_penetrance(genes, alias_genes, hpo_lines):
    """Add information of incomplete penetrance"""
    LOG.info("Add incomplete penetrance info")
    for hgnc_symbol in get_incomplete_penetrance_genes(hpo_lines):
        for hgnc_id in get_correct_ids(hgnc_symbol, alias_genes):
            genes[hgnc_id]["incomplete_penetrance"] = True


def get_correct_ids(hgnc_symbol, alias_genes):
    """Try to get the correct gene based on hgnc_symbol

    The HGNC symbol is unfortunately not a persistent gene identifier.
    Many of the resources that are used by Scout only provides the hgnc symbol to
    identify a gene. We need a way to guess what gene is pointed at.

    Args:
        hgnc_symbol(str): The symbol used by a resource
        alias_genes(dict): A dictionary with all the alias symbols (including the current symbol)
                           for all genes

    Returns:
        hgnc_ids(iterable(int)): Hopefully only one but a symbol could map to several ids
    """
    hgnc_ids = set()
    hgnc_symbol = hgnc_symbol.upper()
    if hgnc_symbol in alias_genes:
        hgnc_id_info = alias_genes[hgnc_symbol]
        if hgnc_id_info["true"]:
            return set([hgnc_id_info["true"]])
        return set(hgnc_id_info["ids"])
    return hgnc_ids


def link_genes(
    ensembl_lines,
    hgnc_lines,
    exac_lines,
    hpo_lines,
    mim2gene_lines=None,
    genemap_lines=None,
):
    """Gather information from different sources and return a gene dict

    Extract information collected from a number of sources and combine them
    into a gene dict with HGNC symbols as keys.

    hgnc_id works as the primary symbol and it is from this source we gather
    as much information as possible (hgnc_complete_set.txt)

    Coordinates are gathered from ensemble and the entries are linked from hgnc
    to ensembl via ENSGID.

    From exac the gene intolerance scores are collected, genes are linked to hgnc
    via hgnc symbol. This is a unstable symbol since they often change.


        Args:
            ensembl_lines(iterable(str)): Strings with ensembl gene information
            hgnc_lines(iterable(str)): Strings with hgnc gene information
            exac_lines(iterable(str)): Strings with exac PLi score info
            mim2gene_lines(iterable(str))
            genemap_lines(iterable(str))
            hpo_lines(iterable(str)): Strings with hpo gene information

        Yields:
            gene(dict): A dictionary with gene information
    """
    genes = {}
    LOG.info("Linking genes")
    # HGNC genes are the main source, these define the gene dataset to use
    # Try to use as much information as possible from hgnc
    for hgnc_gene in parse_hgnc_genes(hgnc_lines):
        hgnc_id = hgnc_gene["hgnc_id"]
        genes[hgnc_id] = hgnc_gene

    add_ensembl_info(genes, ensembl_lines)

    symbol_to_id = genes_by_alias(genes)

    add_exac_info(genes, symbol_to_id, exac_lines)

    add_incomplete_penetrance(genes, symbol_to_id, hpo_lines)

    if mim2gene_lines and genemap_lines:
        add_omim_info(genes, symbol_to_id, genemap_lines, mim2gene_lines)

    return genes
