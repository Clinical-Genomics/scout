# igv.js track settings common for all users and all cases
HG19REF_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg19/hg19.fasta"
HG19REF_INDEX_URL = (
    "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg19/hg19.fasta.fai"
)
HG19CYTOBAND_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg19/cytoBand.txt"
HG38REF_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa"
HG38REF_INDEX_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa.fai"
HG38CYTOBAND_URL = (
    "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg38/cytoBandIdeo.txt"
)

HG38GENES_FORMAT = "gtf"
HG38GENES_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg38/genes/Homo_sapiens.GRCh38.80.sorted.gtf.gz"
HG38GENES_INDEX_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg38/genes/Homo_sapiens.GRCh38.80.sorted.gtf.gz.tbi"
HG19GENES_FORMAT = "bed"
HG19GENES_URL = (
    "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg19/genes/refGene.hg19.bed.gz"
)
HG19GENES_INDEX_URL = (
    "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg19/genes/refGene.hg19.bed.gz.tbi"
)

HG38CLINVAR_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg38/bbi/clinvar/clinvarMain.bb"
HG19CLINVAR_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg19/bbi/clinvar/clinvarMain.bb"

HG38CLINVAR_CNVS_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg38/bbi/clinvar/clinvarCnv.bb"
HG19CLINVAR_CNVS_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg19/bbi/clinvar/clinvarCnv.bb"

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
HUMAN_GENES_37 = {
    "name": "Genes",
    "track_name": "genes_track",
    "type": "annotation",
    "sourceType": "file",
    "displayMode": "EXPANDED",
    "format": HG19GENES_FORMAT,
    "url": HG19GENES_URL,
    "indexURL": HG19GENES_INDEX_URL,
}

# Human genes track, build 38
HUMAN_GENES_38 = {
    "name": "Genes",
    "track_name": "genes_track",
    "type": "annotation",
    "sourceType": "file",
    "displayMode": "EXPANDED",
    "format": HG38GENES_FORMAT,
    "url": HG38GENES_URL,
    "indexURL": HG38GENES_INDEX_URL,
}

CASE_SPECIFIC_TRACKS = {
    "rhocall_bed": "Rhocall Zygosity",
    "rhocall_wig": "Rhocall Regions",
    "tiddit_coverage_wig": "TIDDIT Coverage",
    "upd_regions_bed": "UPD regions",
    "upd_sites_bed": "UPD sites",
}

HUMAN_REFERENCE = {"37": HUMAN_REFERENCE_37, "38": HUMAN_REFERENCE_38}

USER_DEFAULT_TRACKS = ["Genes", "ClinVar", "ClinVar CNVs"]

# Export selectable custom tracks into lists
IGV_TRACKS = {
    "37": [HUMAN_GENES_37, CLINVAR_SNV_37, CLINVAR_CNV_37],
    "38": [HUMAN_GENES_38, CLINVAR_SNV_38, CLINVAR_CNV_38],
}
