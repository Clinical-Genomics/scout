EXPORT_HEADER = [
    "Rank_score",
    "Chromosome",
    "Position",
    "Change",
    "Position_Change",
    "HGNC_id",
    "Gene_name",
    "Canonical_transcript",
    "Canonical_transcript_HGVS",
    "Canonical_transcript_protein_change",
]

MT_EXPORT_HEADER = [
    "Position",
    "Change",
    "Position+Change",
    "Gene",
    "HGVS Description",
    "AD Reference",
    "AD Alternative",
]

MT_COV_STATS_HEADER = ["Mean MT coverage", "Mean chrom 14 scoverage", "Estimated mtDNA copy number"]

VCF_HEADER = [
    "##fileformat=VCFv4.2",
    '##INFO=<ID=END,Number=1,Type=Integer,Description="End position of the variant described in this record">',
    '##INFO=<ID=SVTYPE,Number=1,Type=String,Description="Type of structural variant">',
    '##INFO=<ID=TYPE,Number=1,Type=String,Description="Type of variant">',
    '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
    "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO",
]

VERIFIED_VARIANTS_HEADER = [
    "Institute",
    "Database id",
    "Variant category",
    "Variant type",
    "Display name",
    "Local link",
    "Verified state",
    "Case name",
    "Sample",
    "Position",
    "Change",
    "Canonical_transcript_HGVS",
    "Functional annotations",
    "Genes",  # This is going to be a list flattened to a string
    "Rank score",
    "CADD score",
    "Sample genotype",
    "AD reference",
    "AD alternative",
    "Genotype quality",
]
