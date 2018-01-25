import logging

from pprint import pprint as pp

logger = logging.getLogger(__name__)

def parse_ensembl_gene_request(result):
    """Parse a dataframe with ensembl gene information
    
    Args:
        res(pandas.DataFrame)
    
    Yields:
        gene_info(dict)
    """
    
    keys = [
        'chrom',
        'gene_start',
        'gene_end',
        'ensembl_gene_id',
        'hgnc_symbol',
        'hgnc_id',
    ]
    # for res in result.itertuples():
    for res in zip(result['Chromosome/scaffold name'], result['Gene start (bp)'], result['Gene end (bp)'],
                    result['Gene stable ID'], result['HGNC symbol'], result['HGNC ID']):
        ensembl_info = dict(zip(keys, res))
        
        if type(ensembl_info['hgnc_symbol']) is float:
            # Skip genes without hgnc information
            continue
        ensembl_info['gene_start'] = int(ensembl_info['gene_start'])
        ensembl_info['gene_end'] = int(ensembl_info['gene_end'])
        
        if type(ensembl_info['hgnc_id']) is float:
            ensembl_info['hgnc_id'] = int(ensembl_info['hgnc_id'])
        else:
            ensembl_info['hgnc_id'] = int(ensembl_info['hgnc_id'].split(':')[-1])

        yield ensembl_info

def parse_ensembl_transcript_request(result):
    """Parse a dataframe with ensembl transcript information
    
    Args:
        res(pandas.DataFrame)
    
    Yields:
        transcript_info(dict)
    """
    keys = [
        'chrom',
        'ensembl_gene_id',
        'ensembl_transcript_id',
        'transcript_start',
        'transcript_end',
        'refseq_mrna',
        'refseq_mrna_predicted',
        'refseq_ncrna',
    ]
    # for res in result.itertuples():
    for res in zip(result['Chromosome/scaffold name'], result['Gene stable ID'], 
                   result['Transcript stable ID'], result['Transcript start (bp)'], 
                   result['Transcript end (bp)'], result['RefSeq mRNA ID'],
                   result['RefSeq mRNA predicted ID'], result['RefSeq ncRNA ID']):
        ensembl_info = dict(zip(keys, res))

        ensembl_info['transcript_start'] = int(ensembl_info['transcript_start'])
        ensembl_info['transcript_end'] = int(ensembl_info['transcript_end'])

        for key in keys[-3:]:
            if type(ensembl_info[key]) is float:
                ensembl_info[key] = None

        yield ensembl_info

def parse_ensembl_line(line, header):
    """Parse an ensembl formated line
    
        Args:
            line(list): A list with ensembl gene info
            header(list): A list with the header info
        
        Returns:
            ensembl_info(dict): A dictionary with the relevant info
    """
    line = line.rstrip().split('\t')
    header = [head.lower() for head in header]
    raw_info = dict(zip(header, line))
    
    ensembl_info = {}
    
    for word in raw_info:
        value = raw_info[word]
        
        if not value:
            continue
        
        if 'chromosome' in word:
            ensembl_info['chrom'] = value
        
        if 'gene' in word:
            if 'id' in word:
                ensembl_info['ensembl_gene_id'] = value
            elif 'start' in word:
                ensembl_info['gene_start'] = int(value)
            elif 'end' in word:
                ensembl_info['gene_end'] = int(value)
        
        if 'hgnc symbol' in word:
            ensembl_info['hgnc_symbol'] = value
        if "gene name" in word:
            ensembl_info['hgnc_symbol'] = value

        if 'hgnc id' in word:
            ensembl_info['hgnc_id'] = int(value.split(':')[-1])
        
        if 'transcript' in word:
            if 'id' in word:
                ensembl_info['ensembl_transcript_id'] = value
            elif 'start' in word:
                ensembl_info['transcript_start'] = int(value)
            elif 'end' in word:
                ensembl_info['transcript_end'] = int(value)
        
        if 'exon' in word:
            if 'start' in word:
                ensembl_info['exon_start'] = int(value)
            elif 'end' in word:
                ensembl_info['exon_end'] = int(value)
            elif 'rank' in word:
                ensembl_info['exon_rank'] = int(value)
                
        
        if 'utr' in word:

            if 'start' in word:
                if '5' in word:
                    ensembl_info['utr_5_start'] = int(value)
                elif '3' in word:
                    ensembl_info['utr_3_start'] = int(value)
            elif 'end' in word:
                if '5' in word:
                    ensembl_info['utr_5_end'] = int(value)
                elif '3' in word:
                    ensembl_info['utr_3_end'] = int(value)
        
        if 'strand' in word:
            ensembl_info['strand'] = int(value)
        
        if 'refseq' in word:
            if 'mrna' in word:
                if 'predicted' in word:
                    ensembl_info['refseq_mrna_predicted'] = value
                else:
                    ensembl_info['refseq_mrna'] = value
                    
        
            if 'ncrna' in word:
                ensembl_info['refseq_ncrna'] = value

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
        
        #File allways start with a header line
        if index == 0:
            header = line.rstrip().split('\t')
            continue
        #After that each line represents a gene
            
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
    logger.debug("Parsing ensembl transcripts...")
    for index,line in enumerate(lines):
        
        #File allways start with a header line
        if index == 0:
            header = line.rstrip().split('\t')
        #After that each line represents a transcript
        else:
            yield parse_ensembl_line(line, header)

def parse_ensembl_exons(lines):
    """Parse lines with ensembl formated exons
        
        This is designed to take a biomart dump with exons from ensembl.
        Check documentation for spec for download
    
        Args:
            lines(iterable(str)): An iterable with ensembl formated exons
        Yields:
            ensembl_gene(dict): A dictionary with the relevant information
    """
    header = []
    logger.debug("Parsing ensembl exons...")
    for index,line in enumerate(lines):
        
        #File allways start with a header line
        if index == 0:
            header = line.rstrip().split('\t')
            continue
        
        exon_info = parse_ensembl_line(line, header)
        chrom = exon_info['chrom']
        start = exon_info['exon_start']
        end = exon_info['exon_end']
        transcript = exon_info['ensembl_transcript_id']
        gene = exon_info['ensembl_gene_id']
        
        rank = exon_info['exon_rank']
        strand = exon_info['strand']
        
        
        # Recalculate start and stop (taking UTR regions into account for end exons)    
        if strand == 1:
            # highest position: start of exon or end of 5' UTR
            # If no 5' UTR make sure exon_start is allways choosen
            start = max(start, exon_info.get('utr_5_end') or -1)
            # lowest position: end of exon or start of 3' UTR
            end = min(end, exon_info.get('utr_3_start') or float('inf'))
        elif strand == -1:
            # highest position: start of exon or end of 3' UTR
            start = max(start, exon_info.get('utr_3_end') or -1)
            # lowest position: end of exon or start of 5' UTR
            end = min(end, exon_info.get('utr_5_start') or float('inf'))
        
        exon_id = "-".join([chrom, str(start), str(end)])
        
        if start > end:
            raise ValueError("ERROR: %s" % exon_id)
        data = {
            "exon_id": exon_id,
            "chrom": chrom,
            "start": start,
            "end": end,
            "transcript": transcript,
            "gene": gene,
            "rank": rank,
        }
        
        yield data












