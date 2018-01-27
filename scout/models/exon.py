"""
Model for Exon collection

the models are here as a reference for how collections look in the database
"""


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
