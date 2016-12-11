import logging

logger = logging.getLogger(__name__)

def export_transcripts(adapter):
    """Export all genes from the database"""
    logger.info("Exporting all transcripts to .bed format")

    for gene in adapter.all_genes():
        for transcript in gene.transcripts:
            transcript_string = ("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}")
            yield transcript_string.format(
                    gene.chromosome,
                    transcript.start,
                    transcript.end,
                    transcript.ensembl_transcript_id,
                    transcript.refseq_id,
                    gene.hgnc_symbol,
                    gene.hgnc_id
                )
    