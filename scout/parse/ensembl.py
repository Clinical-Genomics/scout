import logging

logger = logging.getLogger(__name__)

def parse_ensembl_line(line, header):
    """Parse an ensembl formated line
    
        Args:
            line(list): A list with ensembl gene info
            header(list): A list with the header info
        
        Returns:
            ensembl_info(dict): A dictionary with the relevant info
    """
    line = line.rstrip().split('\t')
    raw_info = dict(zip(header, line))
    chrom = None
    gene_start = None
    gene_end = None
    transcript_start = None
    transcript_end = None
    hgnc_symbol = None
    ensembl_gene_id = None
    ensembl_transcript_id = None
    refseq_mrna = None
    refseq_mrna_predicted = None
    refseq_ncrna_predicted = None
    refseq_ncrna = None
    
    for word in raw_info:
        if 'Gene ID' in word:
            ensembl_gene_id = raw_info[word]
        if 'Chromosome' in word:
            chrom = raw_info[word]
        if 'Gene Start' in word:
            gene_start = int(raw_info[word])
        if 'Gene End' in word:
            gene_end = int(raw_info[word])
        if 'HGNC symbol' in word:
            hgnc_symbol = raw_info[word]
        if "Associated Gene Name" in word:
            hgnc_symbol = raw_info[word]
        if 'Transcript ID' in word:
            ensembl_transcript_id = raw_info[word]
        if 'Transcript Start' in word:
            transcript_start = int(raw_info[word])
        if 'Transcript End' in word:
            transcript_end = int(raw_info[word])
        if 'RefSeq mRNA' in word:
            if 'predicted' in word:
                refseq_mrna_predicted = raw_info[word]
            else:
                refseq_mrna = raw_info[word]
        if 'RefSeq ncRNA' in word:
            if 'predicted' in word:
                refseq_ncrna_predicted = raw_info[word]
            else:
                refseq_ncrna = raw_info[word]
        
    ensembl_info = {
        'chrom': chrom,
        'gene_start': gene_start,
        'gene_end': gene_end,
        'transcript_start': transcript_start,
        'transcript_end': transcript_end,
        'refseq_mrna': refseq_mrna,
        'refseq_mrna_predicted': refseq_mrna_predicted,
        'refseq_ncrna': refseq_ncrna,
        'refseq_ncrna_predicted': refseq_ncrna_predicted,
        'hgnc_symbol': hgnc_symbol,
        'ensembl_gene_id': ensembl_gene_id,
        'ensembl_transcript_id': ensembl_transcript_id,
    }
    return ensembl_info

def parse_ensembl_genes(lines):
    """Parse lines with ensembl formated genes
        
        This is designed to take a biomart dump with genes from ensembl.
        Mandatory columns are:
        'Gene ID' 'Chromosome' 'Gene Start' 'Gene End' 'HGNC symbol
    
        Args:
            lines(iterable(str)): An iterable with ensembl formated genes
        Yields:
            ensembl_gene(dict): A dictionary with the relevant information
    """
    header = []
    for index,line in enumerate(lines):
        line = line.rstrip().split('\t')
        
        #File allways start with a header line
        if index == 0:
            header = line
        #After that each line represents a gene
        else:
            
            yield parse_ensembl_line(line, header)

def parse_ensembl_transcripts(lines):
    """Parse lines with ensembl formated transcripts
        
        This is designed to take a biomart dump with transcripts from ensembl.
        Mandatory columns are:
        'Gene ID' 'Transcript ID' 'Transcript Start' 'Transcript End' 'RefSeq mRNA'
    
        Args:
            lines(iterable(str)): An iterable with ensembl formated genes
        Yields:
            ensembl_gene(dict): A dictionary with the relevant information
    """
    header = []
    logger.info("Parsing ensembl transcripts...")
    for index,line in enumerate(lines):
        
        #File allways start with a header line
        if index == 0:
            header = line.rstrip().split('\t')
        #After that each line represents a transcript
        else:
            yield parse_ensembl_line(line, header)
