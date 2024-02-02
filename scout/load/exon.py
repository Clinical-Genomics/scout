import logging
from datetime import datetime

from click import progressbar

from scout.build.genes.exon import build_exon
from scout.parse.ensembl import parse_ensembl_exons

LOG = logging.getLogger(__name__)


def load_exons(adapter, exon_lines, build="37", nr_exons=None):
    """Build and load all the exons of a build

    Transcript information is from ensembl.

    First check that the gene that the transcript belongs to exist in the database.
    If so check that the exon belongs to one of the identifier transcripts of that gene.

    Args:
        adapter(MongoAdapter)
        exon_lines(iterable): iterable with ensembl exon lines
        build(str)

    """
    nr_exons = nr_exons or 100000
    # Fetch all genes with ensemblid as keys
    ensembl_genes = adapter.ensembl_genes(build=build, id_transcripts=True)

    LOG.debug("Parsing ensembl exons from iterable")
    exons = parse_ensembl_exons(exon_lines)

    start_insertion = datetime.now()
    loaded_exons = 0
    exon_bulk = []
    LOG.info("Loading exons...")
    current_chrom = None
    with progressbar(exons, label="Loading exons", length=nr_exons) as bar:
        for exon in bar:
            ensg_id = exon["gene"]
            enst_id = exon["transcript"]
            gene_obj = ensembl_genes.get(ensg_id)
            if not gene_obj:
                continue

            hgnc_id = gene_obj["hgnc_id"]

            if not enst_id in gene_obj.get("id_transcripts", set()):
                continue

            exon_id = exon["exon_id"]

            exon["hgnc_id"] = hgnc_id

            exon_obj = build_exon(exon, build)
            exon_bulk.append(exon_obj)
            if len(exon_bulk) > 10000:
                adapter.load_exon_bulk(exon_bulk)
                exon_bulk = []
            loaded_exons += 1

    if exon_bulk:
        adapter.load_exon_bulk(exon_bulk)

    LOG.info("Number of exons in build {0}: {1}".format(build, nr_exons))
    LOG.info("Number loaded: {0}".format(loaded_exons))
    LOG.info("Time to load exons: {0}".format(datetime.now() - start_insertion))
