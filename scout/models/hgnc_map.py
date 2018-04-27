from __future__ import unicode_literals

from bson.objectid import ObjectId

class Exon(dict):
    """Exon dictionary
    
        "exon_id": str, # str(chrom-start-end)
        "chrom": str, 
        "start": int, 
        "end": int,     
        "transcript": str, # ENST ID
        "hgnc_id": int,      # HGNC_id
        "rank": int, # Order of exon in transcript
        "build": str, # Genome build
    
    """
    def __init__(self, exon_id, chrom, start, end, transcript, hgnc_id, rank, build='37'):
        super(Exon, self).__init__()
        self['exon_id'] = exon_id
        self['chrom'] = chrom
        self['start'] = int(start)
        self['end'] = int(end)
        self['transcript'] = transcript
        self['hgnc_id'] = hgnc_id
        self['rank'] = int(rank)
        self['build'] = build

class HgncTranscript(dict):
    """Transcript dictionary
    
        "transcript_id": str, # ensembl id
        "hgnc_id": int,
        "chrom": str, 
        "start": int, 
        "end": int, 
        "is_primary": bool, 
        "refseq_id": str, 
        "build": str, # Genome build
        "length": int
    """
    def __init__(self, transcript_id, hgnc_id, chrom, start, end, is_primary=False, 
                 refseq_id=None, build='37'):
        super(HgncTranscript, self).__init__()
        self['transcript_id'] = transcript_id
        self['hgnc_id'] = int(hgnc_id)
        self['chrom'] = chrom
        self['start'] = int(start)
        self['end'] = int(end)
        self['is_primary'] = is_primary
        self['refseq_id'] = refseq_id
        self['build'] = build
        self['length'] = self['end'] - self['start']


hgnc_gene = {
                '_id': ObjectId(),
                'hgnc_id': int, # This is the hgnc id, required:
                'hgnc_symbol': str, # The primary symbol, required 
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
                
                # Inheritance information
                'inheritance_models': list(), # List of model names
                'incomplete_penetrance': bool, # Acquired from HPO
                
                # Phenotype information
                'phenotypes': list(), # List of dictionaries with phenotype information
    }
