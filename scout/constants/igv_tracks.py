# igv.js track settings common for all users and all cases
HG19REF_URL = (
    "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/1kg_v37/human_g1k_v37_decoy.fasta"
)
HG19REF_INDEX_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/1kg_v37/human_g1k_v37_decoy.fasta.fai"
HG19CYTOBAND_URL = "https://raw.githubusercontent.com/Clinical-Genomics/reference-files/refs/heads/master/rare-disease/region/grch37_cytoband.bed"
HG19ALIAS_URL = "https://igv.org/genomes/data/hg19/hg19_alias.tab"

HG38REF_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa"
HG38REF_INDEX_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa.fai"
HG38ALIAS_URL = "https://igv.org/genomes/data/hg38/hg38_alias.tab"
HG38CYTOBAND_URL = "https://igv-genepattern-org.s3.amazonaws.com/genomes/hg38/cytoBandIdeo.txt.gz"

HG38GENES_URL = "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/ncbiRefSeq.txt.gz"
HG38GENES_FORMAT = "refgene"

HG19GENES_URL = "https://s3.amazonaws.com/igv.org.genomes/hg19/ncbiRefSeq.sorted.txt.gz"
HG19GENES_INDEX_URL = "https://s3.amazonaws.com/igv.org.genomes/hg19/ncbiRefSeq.sorted.txt.gz.tbi"
HG19GENES_FORMAT = "refgene"

HG38CLINVAR_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg38/bbi/clinvar/clinvarMain.bb"
HG19CLINVAR_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg19/bbi/clinvar/clinvarMain.bb"

HG38CLINVAR_SVS_URL = (
    "https://ftp.ncbi.nlm.nih.gov/pub/dbVar/sandbox/dbvarhub/hg38/clinvar_pathogenic.bb"
)
HG19CLINVAR_SVS_URL = (
    "https://ftp.ncbi.nlm.nih.gov/pub/dbVar/sandbox/dbvarhub/hg19/clinvar_pathogenic.bb"
)

# Human genome reference genome build 37. Always displayed
HUMAN_REFERENCE_37 = {
    "id": "hg19",
    "fastaURL": HG19REF_URL,
    "indexURL": HG19REF_INDEX_URL,
    "cytobandURL": HG19CYTOBAND_URL,
    "aliasURL": HG19ALIAS_URL,
}

# Human genome reference genome build 38. Always displayed
HUMAN_REFERENCE_38 = {
    "id": "hg38",
    "fastaURL": HG38REF_URL,
    "indexURL": HG38REF_INDEX_URL,
    "cytobandURL": HG38CYTOBAND_URL,
    "aliasURL": HG38ALIAS_URL,
}

# igv.js track settings common for all users and all cases. Selectable by users
# Clinvar SNVs track genome build 37
CLINVAR_SNV_37 = {
    "name": "ClinVar",
    "track_name": "clinvar_snvs",
    "type": "annotation",
    "sourceType": "file",
    "displayMode": "EXPANDED",
    "visibilityWindow": 300000,
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
    "visibilityWindow": 300000,
    "format": "bigBed",
    "maxRows": 30,
    "url": HG38CLINVAR_URL,
}

# ClinVar CNVs track genome build 37
CLINVAR_SV_37 = {
    "name": "ClinVar SVs",
    "track_name": "clinvar_svs",
    "type": "annotation",
    "sourceType": "file",
    "displayMode": "SQUISHED",
    "visibilityWindow": 3000000000,
    "format": "bigBed",
    "height": 100,
    "url": HG19CLINVAR_SVS_URL,
}

# ClinVar CNVs track genome build 38
CLINVAR_SV_38 = {
    "name": "ClinVar SVs",
    "track_name": "clinvar_svs",
    "type": "annotation",
    "sourceType": "file",
    "displayMode": "SQUISHED",
    "visibilityWindow": 3000000000,
    "format": "bigBed",
    "height": 100,
    "url": HG38CLINVAR_SVS_URL,
}

# Human genes track, build 37
HUMAN_GENES_37 = {
    "name": "Genes",
    "type": "annotation",
    "sourceType": "file",
    "displayMode": "EXPANDED",
    "visibilityWindow": 300000000,
    "format": HG19GENES_FORMAT,
    "url": HG19GENES_URL,
    "indexURL": HG19GENES_INDEX_URL,
}

# Human genes track, build 38
HUMAN_GENES_38 = {
    "name": "Genes",
    "type": "annotation",
    "sourceType": "file",
    "displayMode": "EXPANDED",
    "visibilityWindow": 300000000,
    "format": HG38GENES_FORMAT,
    "url": HG38GENES_URL,
    "order": 1000000,
}

CASE_SPECIFIC_TRACKS = {
    "paraphase_alignments": "Paraphase Alignment",
    "assembly_alignments": "de novo Assembly Alignment",
    "minor_allele_frequency_wigs": "SV Caller Minor Allele Frequency",
    "rhocall_beds": "Rhocall Zygosity",
    "rhocall_wigs": "Rhocall Regions",
    "tiddit_coverage_wigs": "SV Caller Coverage",
    "upd_regions_beds": "UPD Regions",
    "upd_sites_beds": "UPD Sites",
}

HUMAN_REFERENCE = {"37": HUMAN_REFERENCE_37, "38": HUMAN_REFERENCE_38}

USER_DEFAULT_TRACKS = ["Genes", "ClinVar", "ClinVar CNVs"]

# Export selectable custom tracks into lists
IGV_TRACKS = {
    "37": [HUMAN_GENES_37, CLINVAR_SNV_37, CLINVAR_SV_37],
    "38": [HUMAN_GENES_38, CLINVAR_SNV_38, CLINVAR_SV_38],
}
