# -*- coding: utf-8 -*-
import logging

from scout.constants import CHROMOSOME_INTEGERS, CHROMOSOMES

LOG = logging.getLogger(__name__)


def export_panels(adapter, panels, versions=None, build="37"):
    """Export all genes in gene panels

    Exports the union of genes in one or several gene panels to a bed like format with coordinates.

    Args:
        adapter(scout.adapter.MongoAdapter)
        panels(iterable(str)): Iterable with panel ids
        bed(bool): If lines should be bed formated
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


def export_gene_panels(adapter, panels, version=None):
    """Export the genes of a gene panel

    Takes a list of gene panel names and return the lines of the gene panels.
    Unlike export_panels this function only export the genes and extra information,
    not the coordinates.

    Args:
        adapter(MongoAdapter)
        panels(list(str))
        version(float): Version number, only works when one panel

    Yields:
        gene panel lines
    """
    if version and len(panels) > 1:
        raise SyntaxError("Version only possible with one panel")

    bed_string = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}"

    headers = []

    # Dictionary with hgnc ids as keys and panel gene information as value.
    panel_geneobjs = dict()

    for panel_id in panels:
        panel_obj = adapter.gene_panel(panel_id, version=version)
        if not panel_obj:
            LOG.warning("Panel %s could not be found", panel_id)
            continue

        for gene_obj in panel_obj["genes"]:
            panel_geneobjs[gene_obj["hgnc_id"]] = gene_obj

    if len(panel_geneobjs) == 0:
        return

    headers.append(
        "#hgnc_id\thgnc_symbol\tdisease_associated_transcripts\t"
        "reduced_penetrance\tmosaicism\tdatabase_entry_version"
    )

    for header in headers:
        yield header

    for hgnc_id in panel_geneobjs:
        gene_obj = panel_geneobjs[hgnc_id]
        gene_line = bed_string.format(
            gene_obj["hgnc_id"],
            gene_obj["symbol"],
            ",".join(gene_obj.get("disease_associated_transcripts", [])),
            gene_obj.get("reduced_penetrance", ""),
            gene_obj.get("mosaicism", ""),
            gene_obj.get("database_entry_version", ""),
        )
        yield gene_line
