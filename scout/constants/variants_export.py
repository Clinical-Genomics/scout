EXPORT_HEADER = [
    'Rank_score',
    'Chromosome',
    'Position',
    'Change',
    'Position_Change',
    'HGNC_id',
    'Gene_name',
    'Canonical_transcript_HGVS'
]

MT_EXPORT_HEADER = [
    'Position',
    'Change',
    'Position+Change',
    'Gene',
    'HGVS Description',
    'AD Reference',
    'AD Alternative'
]

VCF_HEADER = [
    '##fileformat=VCFv4.2',
    '##INFO=<ID=END,Number=1,Type=Integer,Description="End position of the variant described in this record">',
    '##INFO=<ID=SVTYPE,Number=1,Type=String,Description="Type of structural variant">',
    '##INFO=<ID=TYPE,Number=1,Type=String,Description="Type of variant">',
    '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
    '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO'
]

VERIFIED_VARIANTS_HEADER= [
    'Database id',
    'Variant category',
    'Variant type',
    'Display name',
    'Verified state',
    'Case name',
    'Institute',
    'Position',
    'Change',
    'Canonical_transcript_HGVS'
    'Genes', # This is going to be a list flattened to a string
    'Protein effect',
    'Variant callers', # This is going to be a list flattened to a string
    'Rank score',
    'CADD score',
    'Samples',
    'Sample genotype', # This is going to be a list flattened to a string
    'Scout link'
]
