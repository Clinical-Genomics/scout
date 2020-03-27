HG19REF_URL = (
    "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg19/hg19.fasta"
)
HG19REF_INDEX_URL = (
    "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg19/hg19.fasta.fai"
)
HG19CYTOBAND_URL = (
    "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg19/cytoBand.txt"
)
HG38REF_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa"
HG38REF_INDEX_URL = (
    "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa.fai"
)
HG38CYTOBAND_URL = (
    "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg38/cytoBandIdeo.txt"
)

HG38GENES_FORMAT = "gtf"
HG38GENES_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg38/genes/Homo_sapiens.GRCh38.80.sorted.gtf.gz"
HG38GENES_INDEX_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg38/genes/Homo_sapiens.GRCh38.80.sorted.gtf.gz.tbi"
HG19GENES_FORMAT = "bed"
HG19GENES_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg19/genes/refGene.hg19.bed.gz"
HG19GENES_INDEX_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg19/genes/refGene.hg19.bed.gz.tbi"

HG38CLINVAR_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg38/bbi/clinvar/clinvarMain.bb"
HG19CLINVAR_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg19/bbi/clinvar/clinvarMain.bb"

HG38CLINVAR_CNVS_URL = (
    "https://hgdownload.soe.ucsc.edu/gbdb/hg38/bbi/clinvar/clinvarCnv.bb"
)
HG19CLINVAR_CNVS_URL = (
    "https://hgdownload.soe.ucsc.edu/gbdb/hg19/bbi/clinvar/clinvarCnv.bb"
)


def clinvar_track(build, chrom):
    """Return a dictionary consisting in the clinVar snvs track

    Accepts:
        build(str): "37" or "38"
        chrom(str)

    Returns:
        clinvar_track(dict)
    """

    clinvar_track = {
        "name": "ClinVar",
        "type": "annotation",
        "sourceType": "file",
        "displayMode": "EXPANDED",
        "format": "bigBed",
        "maxRows": 30,
    }
    if build in ["GRCh38", "38"] or chrom == "M":
        clinvar_track["url"] = HG38CLINVAR_URL
    else:
        clinvar_track["url"] = HG19CLINVAR_URL

    return clinvar_track


def clinvar_cnvs_track(build, chrom):
    """Return a dictionary consisting in the clinVar SVs track

    Accepts:
        build(str): "37" or "38"
        chrom(str)

    Returns:
        clinvar_cnvs_track(dict)
    """
    clinvar_cnvs_track = {
        "name": "ClinVar CNVs",
        "type": "annotation",
        "sourceType": "file",
        "displayMode": "SQUISHED",
        "format": "bigBed",
        "height": 100,
    }

    if build in ["GRCh38", "38"] or chrom == "M":
        clinvar_cnvs_track["url"] = HG38CLINVAR_CNVS_URL
    else:
        clinvar_cnvs_track["url"] = HG19CLINVAR_CNVS_URL

    return clinvar_cnvs_track


def reference_track(build, chrom):
    """Return a dictionary consisting in the igv.js genome reference track

    Accepts:
        build(str): "37" or "38"
        chrom(str)

    Returns:
        reference_track(dict)
    """
    reference_track = {}

    if build in ["GRCh38", "38"] or chrom == "M":
        reference_track["fastaURL"] = HG38REF_URL
        reference_track["indexURL"] = HG38REF_INDEX_URL
        reference_track["cytobandURL"] = HG38CYTOBAND_URL
    else:
        reference_track["fastaURL"] = HG19REF_URL
        reference_track["indexURL"] = HG19REF_INDEX_URL
        reference_track["cytobandURL"] = HG19CYTOBAND_URL

    return reference_track


def genes_track(build, chrom):
    """Return a dictionary consisting in the igv.js genes track

    Accepts:
        build(str): "37" or "38"
        chrom(str)

    Returns:
        genes_track(dict)
    """
    genes_track = {
        "name": "Genes",
        "type": "annotation",
        "sourceType": "file",
        "displayMode": "EXPANDED",
    }

    if build in ["GRCh38", "38"] or chrom == "M":
        genes_track["format"] = HG38GENES_FORMAT
        genes_track["url"] = HG38GENES_URL
        genes_track["indexURL"] = HG38GENES_INDEX_URL
    else:
        genes_track["format"] = HG19GENES_FORMAT
        genes_track["url"] = HG19GENES_URL
        genes_track["indexURL"] = HG19GENES_INDEX_URL

    return genes_track
