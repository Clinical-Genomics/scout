import logging

from scout.parse.hgnc import parse_hgnc_genes
from scout.parse.ensembl import parse_ensembl_transcripts
from scout.parse.exac import parse_exac_genes
from scout.parse.hpo import parse_hpo_genes

logger = logging.getLogger(__name__)


def add_gene_coordinates(gene, transcript):
    """Add the gene coordinated"""
    gene['ensembl_gene_id'] = transcript['ensembl_gene_id']
    gene['chromosome'] = transcript['chrom']
    gene['start'] = transcript['gene_start']
    gene['end'] = transcript['gene_end']


def add_transcript(gene, parsed_transcript):
    """Add a transcript to a gene if it is not already there"""
    if parsed_transcript:
        refseq_identifyer = parsed_transcript['refseq']
        enstid = parsed_transcript['enst_id']
        # If the transcript is already added
        if enstid in gene['transcripts']:
            # We check if the current transcript is one of the identifiers
            if refseq_identifyer:
                # print(refseq_identifyer, gene['ref_seq'])
                if refseq_identifyer in gene['ref_seq']:
                    gene['transcripts'][enstid] = parsed_transcript
        else:
            gene['transcripts'][enstid] = parsed_transcript


def link_genes(ensembl_lines, hgnc_lines, exac_lines, hpo_lines):
    """Gather information from different sources and return a gene dict

        Extract information collected from a number of sources and combine them
        into a gene dict with HGNC symbols as keys.

        Args:
            ensembl_lines(iterable(str))
            hgnc_lines(iterable(str))
            exac_lines(iterable(str))
            hpo_lines(iterable(str))

        Yields:
            gene(dict): A dictionary with gene information
    """
    genes = {}
    gene_aliases = {}
    logger.info("Linking genes and transcripts")
    # HGNC genes are the main source, these define the gene dataset to use
    for hgnc_gene in parse_hgnc_genes(hgnc_lines):
        hgnc_symbol = hgnc_gene['hgnc_symbol']
        hgnc_id = hgnc_gene['hgnc_id']
        aliases = hgnc_gene['previous']
        gene = {}
        gene['hgnc_id'] = hgnc_id
        gene['hgnc_symbol'] = hgnc_symbol
        gene['previous_symbols'] = hgnc_gene['previous']
        gene['description'] = hgnc_gene['description']
        gene['omim_ids'] = hgnc_gene['omim_ids']
        gene['entrez_id'] = hgnc_gene['entrez_id']
        gene['ref_seq'] = hgnc_gene['ref_seq']
        gene['uniprot_ids'] = hgnc_gene['uniprot_ids']
        gene['ucsc_id'] = hgnc_gene['ucsc_id']
        gene['vega_id'] = hgnc_gene['vega_id']
        gene['transcripts'] = {}
        genes[hgnc_symbol] = gene
        for old_symbol in aliases:
            if old_symbol != hgnc_symbol:
                if old_symbol in gene_aliases:
                    gene_aliases[old_symbol].append(hgnc_symbol)
                else:
                    gene_aliases[old_symbol] = [hgnc_symbol]

    # Parse and add the ensembl gene info
    for transcript in parse_ensembl_transcripts(ensembl_lines):
        logger.debug("Found transcript with ensembl id %s" %
                     transcript['ensembl_transcript_id'])

        hgnc_symbol = transcript['hgnc_symbol']

        parsed_transcript = {}
        refseq_identifyer = None
        if transcript['refseq_mrna']:
            refseq_identifyer = transcript['refseq_mrna']
        elif transcript['refseq_ncrna']:
            refseq_identifyer = transcript['refseq_ncrna']
        elif transcript['refseq_mrna_predicted']:
            refseq_identifyer = transcript['refseq_mrna_predicted']

        parsed_transcript['enst_id'] = transcript['ensembl_transcript_id']
        parsed_transcript['refseq'] = refseq_identifyer
        parsed_transcript['start'] = transcript['transcript_start']
        parsed_transcript['end'] = transcript['transcript_end']

        # First check if the symbol is one if the current symbols
        if hgnc_symbol in genes:
            gene = genes[hgnc_symbol]
            add_gene_coordinates(gene, transcript)
            add_transcript(gene, parsed_transcript)

        else:
            if hgnc_symbol in gene_aliases:
                for gene_symbol in gene_aliases[hgnc_symbol]:
                    gene = genes[gene_symbol]

                    if not gene.get('ensembl_gene_id'):
                        add_gene_coordinates(gene, transcript)
                        add_transcript(gene, parsed_transcript)

    for exac_gene in parse_exac_genes(exac_lines):
        hgnc_symbol = exac_gene['hgnc_symbol']
        if hgnc_symbol in genes:
            gene = genes[hgnc_symbol]
            gene['pli_score'] = exac_gene['pli_score']
        else:
            if hgnc_symbol in gene_aliases:
                for gene_symbol in gene_aliases[hgnc_symbol]:
                    gene = genes[gene_symbol]
                    if 'pli_score' not in gene:
                        gene['pli_score'] = exac_gene['pli_score']

    hpo_genes = parse_hpo_genes(hpo_lines)
    for hgnc_symbol in hpo_genes:
        hpo_info = hpo_genes[hgnc_symbol]
        if hgnc_symbol in genes:
            gene = genes[hgnc_symbol]
            if hpo_info.get('incomplete_penetrance'):
                gene['incomplete_penetrance'] = True
            if hpo_info.get('ar'):
                gene['ar'] = True
            if hpo_info.get('ad'):
                gene['ad'] = True
            if hpo_info.get('mt'):
                gene['mt'] = True
            if hpo_info.get('xd'):
                gene['xd'] = True
            if hpo_info.get('xr'):
                gene['xr'] = True
            if hpo_info.get('x'):
                gene['x'] = True
            if hpo_info.get('y'):
                gene['y'] = True

    return genes
