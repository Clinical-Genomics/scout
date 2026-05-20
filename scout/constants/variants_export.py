EXPORT_HEADER = [
    "Rank_score",
    "Type",
    "Callers",
    "Chromosome",
    "Position",
    "Change",
    "Position_Change",
    "HGNC_id",
    "Gene_name",
    "Canonical_transcript/HGVS/protein_change",
    "Primary_transcript/HGVS/protein_change",
    "Consequence",
    "CADD",
    "GnomAD AF",
]

CANCER_EXPORT_HEADER = EXPORT_HEADER + ["VAF TUMOR", "VAF NORMAL", "COSMIC ID"]

FUSION_EXPORT_HEADER = EXPORT_HEADER + [
    "Fusion genes",
    "Orientation",
    "Frame status",
    "Observed",
    "Exon",
    "Junction reads",
    "Split reads",
    "FFPM",
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

MT_COV_STATS_HEADER = [
    "Mean MT coverage",
    "Mean chrom 14 scoverage",
    "Estimated mtDNA copy number",
]

MITODEL_HEADER = [
    "Normal MT read pair count",
    "Discordant MT read pair count",
    "MT discordant ratio (ppk)",
]

VCF_HEADER = [
    "##fileformat=VCFv4.2",
    '##INFO=<ID=END,Number=1,Type=Integer,Description="End position of the variant described in this record">',
    '##INFO=<ID=SVTYPE,Number=1,Type=String,Description="Type of structural variant">',
    '##INFO=<ID=TYPE,Number=1,Type=String,Description="Type of variant">',
    '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
]

CONTIG_LENGTHS = {
    "37": {
        "1": 249250621,
        "2": 243199373,
        "3": 198022430,
        "4": 191154276,
        "5": 180915260,
        "6": 171115067,
        "7": 159138663,
        "8": 146364022,
        "9": 141213431,
        "10": 135534747,
        "11": 135006516,
        "12": 133851895,
        "13": 115169878,
        "14": 107349540,
        "15": 102531392,
        "16": 90354753,
        "17": 81195210,
        "18": 78077248,
        "19": 59128983,
        "20": 63025520,
        "21": 48129895,
        "22": 51304566,
        "X": 155270560,
        "Y": 59373566,
        "M": 16569,
    },
    # hg38 / GRCh38 sizes
    "38": {
        "1": 248956422,
        "2": 242193529,
        "3": 198295559,
        "4": 190214555,
        "5": 181538259,
        "6": 170805979,
        "7": 159345973,
        "8": 145138636,
        "9": 138394717,
        "10": 133797422,
        "11": 135086622,
        "12": 133275309,
        "13": 114364328,
        "14": 107043718,
        "15": 101991189,
        "16": 90338345,
        "17": 83257441,
        "18": 80373285,
        "19": 58617616,
        "20": 64444167,
        "21": 46709983,
        "22": 50818468,
        "X": 156040895,
        "Y": 57227415,
        "M": 16569,
    },
}

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

# Maximum number of exported variants
EXPORTED_VARIANTS_LIMIT = 500
