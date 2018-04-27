import logging

from scout.models.exon import Exon

LOG = logging.getLogger(__name__)

def build_exon(exon_info, build='37'):
    """Build a Exon object object

        Args:
            exon_info(dict): Exon information

        Returns:
            exon_obj(Exon)
        
        "exon_id": str, # str(chrom-start-end)
        "chrom": str, 
        "start": int, 
        "end": int,     
        "transcript": str, # ENST ID
        "gene": int,      # HGNC_id
        "rank": int, # Order of exon in transcript
        "build": str, # Genome build
    """

    try:
        chrom = exon_info['chrom']
    except KeyError:
        raise KeyError("Exons has to have a chromosome")

    try:
        start = int(exon_info['start'])
    except KeyError:
        raise KeyError("Exon has to have a start")
    except TypeError:
        raise TypeError("Exon start has to be integer")
    
    try:
        end = int(exon_info['end'])
    except KeyError:
        raise KeyError("Exon has to have a end")
    except TypeError:
        raise TypeError("Exon end has to be integer")

    try:
        rank = int(exon_info['rank'])
    except KeyError:
        raise KeyError("Exon has to have a rank")
    except TypeError:
        raise TypeError("Exon rank has to be integer")

    try:
        exon_id = exon_info['exon_id']
    except KeyError:
        raise KeyError("Exons has to have a id")

    try:
        transcript = exon_info['transcript']
    except KeyError:
        raise KeyError("Exons has to have a transcript")

    try:
        hgnc_id = int(exon_info['hgnc_id'])
    except KeyError:
        raise KeyError("Exons has to have a hgnc_id")
    except TypeError:
        raise TypeError("hgnc_id has to be integer")

    exon_obj = Exon(
        exon_id = exon_id,
        chrom = chrom,
        start = start,
        end = end,
        rank = rank,
        transcript = transcript,
        hgnc_id = hgnc_id,
        build = build,
    )

    return exon_obj
    


def build_hgnc_transcript(transcript_info, build='37'):
    """Build a hgnc_transcript object

        Args:
            transcript_info(dict): Transcript information

        Returns:
            transcript_obj(HgncTranscript)
            {
                transcript_id: str, required
                hgnc_id: int, required
                build: str, required
                refseq_id: str,
                chrom: str, required
                start: int, required
                end: int, required
                is_primary: bool
            }
    """
    try:
        transcript_obj = {'transcript_id':transcript_info['transcript']}
    except KeyError:
        raise KeyError("Transcript has to have ensembl id")
    
    transcript_obj['build'] = build
    transcript_obj['is_primary'] = transcript_info.get('is_primary', False)
    
    if transcript_info.get('refseq_id'):
        transcript_obj['refseq_id'] = transcript_info['refseq_id']
    

    try:
        transcript_obj['chrom'] = transcript_info['chrom']
    except KeyError:
        raise KeyError("Transcript has to have a chromosome")
    
    try:
        transcript_obj['start'] = int(transcript_info['start'])
    except KeyError:
        raise KeyError("Transcript has to have start")
    except TypeError:
        raise TypeError("Transcript start has to be integer")

    try:
        transcript_obj['end'] = int(transcript_info['end'])
    except KeyError:
        raise KeyError("Transcript has to have end")
    except TypeError:
        raise TypeError("Transcript end has to be integer")

    try:
        transcript_obj['hgnc_id'] = int(transcript_info['hgnc_id'])
    except KeyError:
        raise KeyError("Transcript has to have a hgnc id")
    except TypeError:
        raise TypeError("hgnc id has to be integer")

    transcript_obj['length'] = transcript_obj['end'] - transcript_obj['start']

    return transcript_obj

def build_phenotype(phenotype_info):
    phenotype_obj = {}
    phenotype_obj['mim_number'] = phenotype_info['mim_number']
    phenotype_obj['description'] = phenotype_info['description']
    phenotype_obj['inheritance_models'] = list(phenotype_info.get('inheritance', set()))
    phenotype_obj['status'] = phenotype_info['status']
    
    return phenotype_obj

def build_hgnc_gene(gene_info, build='37'):
    """Build a hgnc_gene object

        Args:
            gene_info(dict): Gene information

        Returns:
            gene_obj(dict)
    
            {
                '_id': ObjectId(),
                # This is the hgnc id, required:
                'hgnc_id': int, 
                # The primary symbol, required 
                'hgnc_symbol': str,
                'ensembl_id': str, # required
                'build': str, # '37' or '38', defaults to '37', required
                
                'chromosome': str, # required
                'start': int, # required
                'end': int, # required
                
                'description': str, # Gene description
                'aliases': list(), # Gene symbol aliases, includes hgnc_symbol, str
                'entrez_id': int,
                'omim_id': int,
                'pli_score': float,
                'primary_transcripts': list(), # List of refseq transcripts (str)
                'ucsc_id': str,
                'uniprot_ids': list(), # List of str
                'vega_id': str,
                'transcripts': list(), # List of hgnc_transcript
                
                # Inheritance information
                'inheritance_models': list(), # List of model names
                'incomplete_penetrance': bool, # Acquired from HPO
                
                # Phenotype information
                'phenotypes': list(), # List of dictionaries with phenotype information
            }
    """
    try:
        gene_obj = {'hgnc_id':int(gene_info['hgnc_id'])}
    except KeyError as err:
        raise KeyError("Gene has to have a hgnc_id")
    except ValueError as err:
        raise ValueError("hgnc_id has to be integer")
    
    try:
        gene_obj['hgnc_symbol'] = gene_info['hgnc_symbol']
    except KeyError as err:
        raise KeyError("Gene has to have a hgnc_symbol")

    try:
        gene_obj['ensembl_id'] = gene_info['ensembl_gene_id']
    except KeyError as err:
        raise KeyError("Gene has to have a ensembl_id")

    try:
        gene_obj['chromosome'] = gene_info['chromosome']
    except KeyError as err:
        raise KeyError("Gene has to have a chromosome")
    
    try:
        gene_obj['start'] = int(gene_info['start'])
    except KeyError as err:
        raise KeyError("Gene has to have a start position")
    except TypeError as err:
        raise TypeError("Gene start has to be a integer")

    try:
        gene_obj['end'] = int(gene_info['end'])
    except KeyError as err:
        raise KeyError("Gene has to have a end position")
    except TypeError as err:
        raise TypeError("Gene end has to be a integer")

    gene_obj['build'] = build
    gene_obj['description'] = gene_info.get('description')
    gene_obj['aliases'] = gene_info.get('previous_symbols', [])
    gene_obj['entrez_id'] = gene_info.get('entrez_id')
    gene_obj['omim_id'] = gene_info.get('omim_id')
    try:
        gene_obj['pli_score'] = float(gene_info.get('pli_score'))
    except TypeError as err:
        gene_obj['pli_score'] = None
    
    primary_transcripts = gene_info.get('ref_seq', [])
    gene_obj['primary_transcripts'] = primary_transcripts
    gene_obj['ucsc_id'] = gene_info.get('ucsc_id')
    gene_obj['uniprot_ids'] = gene_info.get('uniprot_ids', [])
    gene_obj['vega_id'] = gene_info.get('vega_id')

    gene_obj['incomplete_penetrance'] = gene_info.get('incomplete_penetrance', False)
    gene_obj['inheritance_models'] = gene_info.get('inheritance_models', [])
    
    phenotype_objs = []
    for phenotype_info in gene_info.get('phenotypes', []):
        phenotype_objs.append(build_phenotype(phenotype_info))
    
    gene_obj['phenotypes'] = phenotype_objs

    return gene_obj
