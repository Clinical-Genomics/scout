import logging

from pprint import pprint as pp

from pandas import DataFrame

LOG = logging.getLogger(__name__)


def parse_transcripts(transcript_lines):
    """Parse and massage the transcript information

    There could be multiple lines with information about the same transcript.
    This is why it is necessary to parse the transcripts first and then return a dictionary
    where all information has been merged.

    Args:
        transcript_lines(): This could be an iterable with strings or a pandas.DataFrame

    Returns:
        parsed_transcripts(dict): Map from enstid -> transcript info
    """
    LOG.info("Parsing transcripts")
    # Parse the transcripts, we need to check if it is a request or a file handle
    if isinstance(transcript_lines, DataFrame):
        transcripts = parse_ensembl_transcript_request(transcript_lines)
    else:
        transcripts = parse_ensembl_transcripts(transcript_lines)

    # Since there can be multiple lines with information about the same transcript
    # we store transcript information in a dictionary for now
    parsed_transcripts = {}
    # Loop over the parsed transcripts
    for tx in transcripts:
        tx_id = tx['ensembl_transcript_id']
        ens_gene_id = tx['ensembl_gene_id']

        # Check if the transcript has been added
        # If not, create a new transcript
        if not tx_id in parsed_transcripts:
            tx_info = {
                'chrom': tx['chrom'],
                'transcript_start': tx['transcript_start'],
                'transcript_end': tx['transcript_end'],
                'mrna': set(),
                'mrna_predicted': set(),
                'nc_rna': set(),
                'ensembl_gene_id': ens_gene_id,
                'ensembl_transcript_id': tx_id,
            }
            parsed_transcripts[tx_id] = tx_info
        
        tx_info = parsed_transcripts[tx_id]
        # Add the ref seq information
        if tx.get('refseq_mrna_predicted'):
            tx_info['mrna_predicted'].add(tx['refseq_mrna_predicted'])
        if tx.get('refseq_mrna'):
            tx_info['mrna'].add(tx['refseq_mrna'])
        if tx.get('refseq_ncrna'):
            tx_info['nc_rna'].add(tx['refseq_ncrna'])

    return parsed_transcripts


def parse_ensembl_gene_request(result):
    """Parse a dataframe with ensembl gene information

    Args:
        res(pandas.DataFrame)

    Yields:
        gene_info(dict)
    """
    LOG.info("Parsing genes from request")

    for index, row in result.iterrows():
        # print(index, row)
        ensembl_info = {}

        # Pandas represents missing data with nan which is a float
        if type(row['hgnc_symbol']) is float:
            # Skip genes without hgnc information
            continue

        ensembl_info['chrom'] = row['chromosome_name']
        ensembl_info['gene_start'] = int(row['start_position'])
        ensembl_info['gene_end'] = int(row['end_position'])
        ensembl_info['ensembl_gene_id'] = row['ensembl_gene_id']
        ensembl_info['hgnc_symbol'] = row['hgnc_symbol']

        hgnc_id = row['hgnc_id']

        if type(hgnc_id) is float:
            hgnc_id = int(hgnc_id)
        else:
            hgnc_id = int(hgnc_id.split(':')[-1])

        ensembl_info['hgnc_id'] = hgnc_id

        yield ensembl_info


def parse_ensembl_transcript_request(result):
    """Parse a dataframe with ensembl transcript information

    Args:
        res(pandas.DataFrame)

    Yields:
        transcript_info(dict)
    """
    LOG.info("Parsing transcripts from request")

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
    for index, row in result.iterrows():
        ensembl_info = {}

        ensembl_info['chrom'] = str(row['chromosome_name'])
        ensembl_info['ensembl_gene_id'] = row['ensembl_gene_id']
        ensembl_info['ensembl_transcript_id'] = row['ensembl_transcript_id']

        ensembl_info['transcript_start'] = int(row['transcript_start'])
        ensembl_info['transcript_end'] = int(row['transcript_end'])

        # Check if refseq data is annotated
        # Pandas represent missing data with nan
        for key in keys[-3:]:
            if type(row[key]) is float:
                ensembl_info[key] = None
            else:
                ensembl_info[key] = row[key]
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
            elif 'id' in word:
                ensembl_info['ensembl_exon_id'] = value
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
    LOG.info("Parsing ensembl genes from file")
    header = []
    for index, line in enumerate(lines):

        # File allways start with a header line
        if index == 0:
            header = line.rstrip().split('\t')
            continue
        # After that each line represents a gene

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
    LOG.info("Parsing ensembl genes from file")
    for index, line in enumerate(lines):

        # File allways start with a header line
        if index == 0:
            header = line.rstrip().split('\t')
        # After that each line represents a transcript
        else:
            yield parse_ensembl_line(line, header)

def parse_exon(chrom, gene, transcript, ens_exon_id, exon_chrom_start, exon_chrom_end,
               five_utr_start, five_utr_end, three_utr_start, three_utr_end, strand, rank):
    """Parse the information from a row with exon data"""
    
    exon = {
        'chrom': str(chrom),
        'gene': gene,
        'transcript': transcript,
        'ens_exon_id': ens_exon_id,
        'exon_chrom_start': exon_chrom_start,
        'exon_chrom_end': exon_chrom_end,
        'strand': strand,
        'rank': rank,
        }
    try:
        exon['5_utr_start'] = int(five_utr_start)
    except (ValueError, TypeError) as e:
        exon['5_utr_start'] = None

    try:
        exon['5_utr_end'] = int(five_utr_end)
    except (ValueError, TypeError) as e:
        exon['5_utr_end'] = None

    try:
        exon['3_utr_start'] = int(three_utr_start)
    except (ValueError, TypeError) as e:
        exon['3_utr_start'] = None

    try:
        exon['3_utr_end'] = int(three_utr_end)
    except (ValueError, TypeError) as e:
        exon['3_utr_end'] = None
    
    # Recalculate start and stop (taking UTR regions into account for end exons)
    if exon['strand'] == 1:
        # highest position: start of exon or end of 5' UTR
        # If no 5' UTR make sure exon_start is allways choosen
        start = max(exon['exon_chrom_start'], exon['5_utr_end'] or -1)
        # lowest position: end of exon or start of 3' UTR
        end = min(exon['exon_chrom_end'], exon['3_utr_start'] or float('inf'))
    elif exon['strand'] == -1:
        # highest position: start of exon or end of 3' UTR
        start = max(exon['exon_chrom_start'], exon['3_utr_end'] or -1)
        # lowest position: end of exon or start of 5' UTR
        end = min(exon['exon_chrom_end'], exon['5_utr_start'] or float('inf'))

    exon['start'] = start
    exon['end'] = end
    exon['exon_id'] = "-".join([str(exon['chrom']), str(start), str(end)])
    
    if start > end:
        raise ValueError("ERROR: %s" % exon_id)
    
    return exon

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
    for index, line in enumerate(lines):

        # File allways start with a header line
        if index == 0:
            header = line.rstrip().split('\t')
            continue

        exon_info = parse_ensembl_line(line, header)
        
        exon = parse_exon(
            chrom=exon_info['chrom'], 
            gene=exon_info['ensembl_gene_id'], 
            transcript=exon_info['ensembl_transcript_id'], 
            ens_exon_id=exon_info['ensembl_exon_id'], 
            exon_chrom_start=exon_info['exon_start'],
            exon_chrom_end=exon_info['exon_end'],
            five_utr_start=exon_info.get('utr_5_start'), 
            five_utr_end=exon_info.get('utr_5_start'), 
            three_utr_start=exon_info.get('utr_3_start'),
            three_utr_end=exon_info.get('utr_3_end'),
            strand=exon_info['strand'],
            rank=exon_info['exon_rank']
        )

        yield exon

def parse_ensembl_exon_request(result):
    """Parse a dataframe with ensembl exon information

    Args:
        res(pandas.DataFrame)

    Yields:
        gene_info(dict)
    """
    exon_columns = [
        'chromosome_name',
        'ensembl_gene_id',
        'ensembl_transcript_id',
        'ensembl_exon_id',
        'exon_chrom_start',
        'exon_chrom_end',
        "5_utr_start",
        "5_utr_end",
        "3_utr_start",
        "3_utr_end",
        "strand",
        "rank"
    ]
    # for res in result.itertuples():
    exons = [parse_exon(row[0], row[1], row[2], row[3], row[4], row[5], row[6], 
             row[7], row[8], row[9], row[10], row[11]) for row in result[exon_columns].values]

    for ensembl_info in exons:

        yield ensembl_info
