import logging

from scout.parse import (parse_hgnc_genes, parse_ensembl_transcripts, 
                         parse_exac_genes, parse_hpo_genes)

logger = logging.getLogger(__name__)

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
    logger.info("Linking genes and transcripts")
    #Parse the ensembl gene info
    for transcript in parse_ensembl_transcripts(ensembl_lines):
        logger.debug("Found transcript with ensembl id %s" % 
                      transcript['ensembl_transcript_id'])
        parsed_transcript = {}
        refseq_identifyer = None
        if transcript['refseq_mrna']:
            refseq_identifyer = transcript['refseq_mrna']
        elif transcript['refseq_ncrna']:
            refseq_identifyer = transcript['refseq_ncrna']
        elif transcript['refseq_mrna_predicted']:
            refseq_identifyer = transcript['refseq_mrna_predicted']
        
        if refseq_identifyer:
            hgnc_symbol = transcript['hgnc_symbol']
            parsed_transcript['ensembl_transcript_id'] = transcript['ensembl_transcript_id']
            parsed_transcript['refseq'] = refseq_identifyer
            parsed_transcript['start'] = transcript['transcript_start']
            parsed_transcript['end'] = transcript['transcript_end']
            
            if hgnc_symbol in genes:
                gene = genes[hgnc_symbol]
                if not refseq_identifyer in gene['transcripts']:
                    gene['transcripts'][refseq_identifyer] = parsed_transcript
            else:
                genes[hgnc_symbol] = {
                    'hgnc_symbol': hgnc_symbol,
                    'ensembl_gene_id': transcript['ensembl_gene_id'],
                    'chromosome': transcript['chrom'],
                    'start': transcript['gene_start'],
                    'end': transcript['gene_end'],
                    'transcripts': {
                        refseq_identifyer: parsed_transcript
                    }
                }

    for hgnc_gene in parse_hgnc_genes(hgnc_lines):
        hgnc_symbol = hgnc_gene['hgnc_symbol']
        if hgnc_symbol in genes:
            gene = genes[hgnc_symbol]
            gene['hgnc_id'] = hgnc_gene['hgnc_id']
            gene['previous_symbols'] = hgnc_gene['previous']
            gene['description'] = hgnc_gene['description']
            gene['omim_ids'] = hgnc_gene['omim_ids']
            gene['entrez_id'] = hgnc_gene['entrez_id']
            gene['ref_seq'] = hgnc_gene['ref_seq']
            gene['uniprot_ids'] = hgnc_gene['uniprot_ids']
            gene['ucsc_id'] = hgnc_gene['ucsc_id']
            gene['vega_id'] = hgnc_gene['vega_id']
    
    for exac_gene in parse_exac_genes(exac_lines):
        hgnc_symbol = exac_gene['hgnc_symbol']
        if hgnc_symbol in genes:
            genes[hgnc_symbol]['pli_score'] = exac_gene['pli_score']
    
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