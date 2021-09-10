# igv.js track settings common for all users and all cases
# ----- Human reference tracks -----
HG19REF_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg19/hg19.fasta"
HG19REF_INDEX_URL = (
    "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg19/hg19.fasta.fai"
)
HG38REF_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa"
HG38REF_INDEX_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa.fai"

# ----- Cytoband tracks -----
HG19CYTOBAND_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg19/cytoBand.txt"
HG38CYTOBAND_URL = (
    "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg38/cytoBandIdeo.txt"
)

# ----- refSeq genes annotation tracks -----
HG19GENES_FORMAT = "bed"
HG19GENES_URL = " https://s3-eu-west-1.amazonaws.com/pfigshare-u-files/30726131/NCBI_Refseq_genes_GRCh37_sorted.bed.gz"
HG19GENES_INDEX_URL = "https://s3-eu-west-1.amazonaws.com/pfigshare-u-files/30726128/NCBI_Refseq_genes_GRCh37_sorted.bed.gz.tbi"
HG38GENES_FORMAT = "bed"
HG38GENES_URL = "https://s3-eu-west-1.amazonaws.com/pfigshare-u-files/30726146/NCBI_Refseq_genes_GRCh38_sorted.bed.gz"
HG38GENES_INDEX_URL = "https://s3-eu-west-1.amazonaws.com/pfigshare-u-files/30726143/NCBI_Refseq_genes_GRCh38_sorted.bed.gz.tbi"

# ----- GenCode genes annotation tracks -----
GENCODE_HG19_GENES_FORMAT = "bed"
GENCODE_HG19_GENES_URL = "https://s3-eu-west-1.amazonaws.com/pfigshare-u-files/30726194/GenCode_comprehensive_genes_v38_lift37_sorted.bed.gz"
GENCODE_HG19_GENES_INDEX_URL = "https://s3-eu-west-1.amazonaws.com/pfigshare-u-files/30726191/GenCode_comprehensive_genes_v38_lift37_sorted.bed.gz.tbi"
GENCODE_HG38_GENES_FORMAT = "bed"
GENCODE_HG38_GENES_URL = "https://s3-eu-west-1.amazonaws.com/pfigshare-u-files/30726227/GenCode_comprehensive_genes_v38_sorted.bed.gz"
GENCODE_HG38_GENES_INDEX_URL = "https://s3-eu-west-1.amazonaws.com/pfigshare-u-files/30726224/GenCode_comprehensive_genes_v38_sorted.bed.gz.tbi"

# ----- ClinVar tracks -----
HG38CLINVAR_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg38/bbi/clinvar/clinvarMain.bb"
HG19CLINVAR_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg19/bbi/clinvar/clinvarMain.bb"
HG38CLINVAR_CNVS_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg38/bbi/clinvar/clinvarCnv.bb"
HG19CLINVAR_CNVS_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg19/bbi/clinvar/clinvarCnv.bb"


# ----- Track objects imported and used in igv.js ------
# Human genome reference genome build 37. Always displayed
HUMAN_REFERENCE_37 = {
    "fastaURL": HG19REF_URL,
    "indexURL": HG19REF_INDEX_URL,
    "cytobandURL": HG19CYTOBAND_URL,
}

# Human genome reference genome build 38. Always displayed
HUMAN_REFERENCE_38 = {
    "fastaURL": HG38REF_URL,
    "indexURL": HG38REF_INDEX_URL,
    "cytobandURL": HG38CYTOBAND_URL,
}

# igv.js track settings common for all users and all cases. Selectable by users
# Clinvar SNVs track genome build 37
CLINVAR_SNV_37 = {
    "name": "ClinVar",
    "track_name": "clinvar_snvs",
    "type": "annotation",
    "sourceType": "file",
    "displayMode": "EXPANDED",
    "format": "bigBed",
    "maxRows": 30,
    "url": HG19CLINVAR_URL,
}

# Clinvar SNVs track genome build 38
CLINVAR_SNV_38 = {
    "name": "ClinVar",
    "track_name": "clinvar_snvs",
    "type": "annotation",
    "sourceType": "file",
    "displayMode": "EXPANDED",
    "format": "bigBed",
    "maxRows": 30,
    "url": HG38CLINVAR_URL,
}

# ClinVar CNVs track genome build 37
CLINVAR_CNV_37 = {
    "name": "ClinVar CNVs",
    "track_name": "clinvar_cnvs",
    "type": "annotation",
    "sourceType": "file",
    "displayMode": "SQUISHED",
    "format": "bigBed",
    "height": 100,
    "url": HG19CLINVAR_CNVS_URL,
}

# ClinVar CNVs track genome build 38
CLINVAR_CNV_38 = {
    "name": "ClinVar CNVs",
    "track_name": "clinvar_cnvs",
    "type": "annotation",
    "sourceType": "file",
    "displayMode": "SQUISHED",
    "format": "bigBed",
    "height": 100,
    "url": HG38CLINVAR_CNVS_URL,
}


# Human genes track, build 37
REFSEQ_GENES_37 = {
    "name": "RefSeq Genes",
    "track_name": "genes_track",
    "type": "annotation",
    "sourceType": "file",
    "displayMode": "EXPANDED",
    "format": HG19GENES_FORMAT,
    "url": HG19GENES_URL,
    "indexURL": HG19GENES_INDEX_URL,
}

# Human genes track, build 38
REFSEQ_GENES_38 = {
    "name": "RefSeq Genes",
    "track_name": "genes_track",
    "type": "annotation",
    "sourceType": "file",
    "displayMode": "EXPANDED",
    "format": HG38GENES_FORMAT,
    "url": HG38GENES_URL,
    "indexURL": HG38GENES_INDEX_URL,
}

GENCODE_GENES_37 = {
    "name": "GenCode Genes",
    "track_name": "gencode_track",
    "type": "annotation",
    "sourceType": "file",
    "displayMode": "EXPANDED",
    "format": GENCODE_HG19_GENES_FORMAT,
    "url": GENCODE_HG19_GENES_URL,
    "indexURL": GENCODE_HG19_GENES_INDEX_URL,
}

GENCODE_GENES_38 = {
    "name": "GenCode Genes",
    "track_name": "gencode_track",
    "type": "annotation",
    "sourceType": "file",
    "displayMode": "EXPANDED",
    "format": GENCODE_HG38_GENES_FORMAT,
    "url": GENCODE_HG38_GENES_URL,
    "indexURL": GENCODE_HG38_GENES_INDEX_URL,
}

CASE_SPECIFIC_TRACKS = {
    "rhocall_bed": "Rhocall Zygosity",
    "rhocall_wig": "Rhocall Regions",
    "tiddit_coverage_wig": "TIDDIT Coverage",
    "upd_regions_bed": "UPD regions",
    "upd_sites_bed": "UPD sites",
}

HUMAN_REFERENCE = {"37": HUMAN_REFERENCE_37, "38": HUMAN_REFERENCE_38}

USER_DEFAULT_TRACKS = ["RefSeq Genes", "GenCode genes", "ClinVar", "ClinVar CNVs"]

# Export selectable custom tracks into lists
IGV_TRACKS = {
    "37": [REFSEQ_GENES_37, GENCODE_GENES_37, CLINVAR_SNV_37, CLINVAR_CNV_37],
    "38": [REFSEQ_GENES_38, GENCODE_GENES_38, CLINVAR_SNV_38, CLINVAR_CNV_38],
}
