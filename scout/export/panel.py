# -*- coding: utf-8 -*-
import logging
from typing import List

from scout.adapter.mongo.base import MongoAdapter
from scout.constants import CHROMOSOME_INTEGERS, CHROMOSOMES
from scout.constants.panels import EXPORT_PANEL_FIELDS

LOG = logging.getLogger(__name__)


def export_panels(adapter, panels, versions=None, build="37"):
    """Export all genes in gene panels

    Exports the union of genes in one or several gene panels to a bed like format with coordinates.

    Args:
        adapter(scout.adapter.MongoAdapter)
        panels(iterable(str)): Iterable with panel ids
    """
    if versions and (len(versions) != len(panels)):
        raise SyntaxError("If version specify for each panel")

    headers = []
    build_string = ("##genome_build={}").format(build)
    headers.append(build_string)
    header_string = "##gene_panel={0},version={1},updated_at={2},display_name={3}"
    contig_string = "##contig={0}"
    bed_string = "{0}\t{1}\t{2}\t{3}\t{4}"

    # Save all gene ids found in the collection if panels
    panel_geneids = set()
    # Save all chromosomes found in the collection if panels
    chromosomes_found = set()
    # Store all hgnc geneobjs
    hgnc_geneobjs = []

    # Loop over the panels
    for i, panel_id in enumerate(panels):
        version = None
        if versions:
            version = versions[i]

        panel_obj = adapter.gene_panel(panel_id, version=version)
        if not panel_obj:
            LOG.warning("Panel {0} version {1} could not be found".format(panel_id, version))
            continue

        headers.append(
            header_string.format(
                panel_obj["panel_name"],
                panel_obj["version"],
                panel_obj["date"].date(),
                panel_obj["display_name"],
            )
        )
        # Collect the hgnc ids from all genes found
        for gene_obj in panel_obj["genes"]:
            panel_geneids.add(gene_obj["hgnc_id"])

    if build == "GRCh38":
        build = "38"

    gene_objs = adapter.hgncid_to_gene(build=build)

    for hgnc_id in panel_geneids:
        hgnc_geneobj = gene_objs.get(hgnc_id)
        if hgnc_geneobj is None:
            LOG.warning("missing HGNC gene: %s", hgnc_id)
            continue
        chrom = hgnc_geneobj["chromosome"]
        start = hgnc_geneobj["start"]
        chrom_int = CHROMOSOME_INTEGERS.get(chrom)

        if not chrom_int:
            LOG.warning("Chromosome %s out of scope", chrom)
            continue

        hgnc_geneobjs.append((chrom_int, start, hgnc_geneobj))
        chromosomes_found.add(chrom)

    # Sort the genes:
    hgnc_geneobjs.sort(key=lambda tup: (tup[0], tup[1]))

    for chrom in CHROMOSOMES:
        if chrom in chromosomes_found:
            if build_string == "##genome_build=GRCh38":
                if chrom == "MT":
                    chrom = "M"
                chrom = "".join(["chr", chrom])
            headers.append(contig_string.format(chrom))

    headers.append("#chromosome\tgene_start\tgene_stop\thgnc_id\thgnc_symbol")

    for header in headers:
        yield header

    for hgnc_gene in hgnc_geneobjs:
        gene_obj = hgnc_gene[-1]
        chrom = gene_obj["chromosome"]
        if build_string == "##genome_build=GRCh38":
            if chrom == "MT":
                chrom = "M"
            chrom = "".join(["chr", chrom])

        gene_line = bed_string.format(
            chrom,
            gene_obj["start"],
            gene_obj["end"],
            gene_obj["hgnc_id"],
            gene_obj["hgnc_symbol"],
        )
        yield gene_line


def set_export_fields(panels: list[str]) -> list[tuple]:
    """Set the field that should be exported for one panel or a list of panels."""

    if len(panels) == 1:
        return EXPORT_PANEL_FIELDS

    # if more than one panel is exported (from the CLI) - export only HGNC and symbol
    return EXPORT_PANEL_FIELDS[:2]


def export_gene_panels(adapter: MongoAdapter, panels: List[str], version: float = None):
    """Export the genes of a gene panel

    Takes a list of gene panel names and return the lines of the gene panels.
    Unlike export_panels this function only export the genes and extra information,
    not the coordinates.

    Yields:
        gene panel lines
    """

    if version and len(panels) > 1:
        raise SyntaxError("Version only possible with one panel")

    # Dictionary with hgnc ids as keys and panel gene information as value.
    panel_geneobjs = dict()

    for panel_id in panels:
        panel_obj = adapter.gene_panel(panel_id, version=version)
        if not panel_obj:
            LOG.warning("Panel %s could not be found", panel_id)
            continue
        panel_geneobjs.update({gene["hgnc_id"]: gene for gene in panel_obj.get("genes", [])})

    if not panel_geneobjs:
        return

    header = []
    header.append("\t".join(fields[0] for fields in EXPORT_PANEL_FIELDS))
    yield from header

    for gene_obj in panel_geneobjs.values():
        gene_line_fields = [
            (
                ",".join(gene_obj.get(gene_key, ""))
                if isinstance(gene_obj.get(gene_key), list)
                else str(gene_obj.get(gene_key, ""))
            )
            for _, gene_key in set_export_fields(panels=panels)
        ]
        yield "\t".join(gene_line_fields)
