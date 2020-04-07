from flask import current_app
from scout.utils.cloud_resources import amazon_s3_url

# Genome reference tracks
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

# Gene tracks
HG38GENES_FORMAT = "gtf"
HG38GENES_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg38/genes/Homo_sapiens.GRCh38.80.sorted.gtf.gz"
HG38GENES_INDEX_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg38/genes/Homo_sapiens.GRCh38.80.sorted.gtf.gz.tbi"
HG19GENES_FORMAT = "bed"
HG19GENES_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg19/genes/refGene.hg19.bed.gz"
HG19GENES_INDEX_URL = "https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg19/genes/refGene.hg19.bed.gz.tbi"


# Clinvar tracks
HG38CLINVAR_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg38/bbi/clinvar/clinvarMain.bb"
HG19CLINVAR_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg19/bbi/clinvar/clinvarMain.bb"
HG38CLINVAR_CNVS_URL = (
    "https://hgdownload.soe.ucsc.edu/gbdb/hg38/bbi/clinvar/clinvarCnv.bb"
)
HG19CLINVAR_CNVS_URL = (
    "https://hgdownload.soe.ucsc.edu/gbdb/hg19/bbi/clinvar/clinvarCnv.bb"
)

# Cosmic tracks
HG19COSMIC_CODING = "CosmicCodingMuts_v90_hg19.vcf.gz"
HG19COSMIC_NON_CODING = "CosmicNonCodingVariants_v90_hg19.vcf.gz"
HG38COSMIC_CODING = "CosmicCodingMuts_v90_hg38.vcf.gz"
HG38COSMIC_NON_CODING = "CosmicNonCodingVariants_v90_hg38.vcf.gz"


def _get_cloud_credentials():
    """Returns cloud S3 storage credentials as a dictionary

    Returns:
        cloud_credentials(list): [endpoint_url, access_key, secrey_access_key, bucket_name]

    """
    cloud_credentials = {
        "region": current_app.config.get("REGION_NAME"),
        "key": current_app.config.get("ACCESS_KEY"),
        "secret_key": current_app.config.get("SECRET_ACCESS_KEY"),
        "bucket": current_app.config.get("BUCKET_NAME"),
        "folder": current_app.config.get("FOLDER_NAME") #Could be None
    }
    return cloud_credentials


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


def cosmic_track(build, chrom, coding=True):
    """Return a dictionary consisting in the cosmic coding track

    Accepts:
        build(str): "37" or "38"
        chrom(str)
        coding(bool): True=cosmic coding, False=cosmic non-coding

    Returns:
        cosmic_track(dict)
    """
    cosmic_track = {
        "name": "Cosmic coding",
        "type": "variant",
        "format": "vcf",
        "displayMode": "squished",
    }
    if coding is False:
        cosmic_track["name"] = "Cosmic non coding"

    track = None
    track_index = None

    if build in ["GRCh38", "38"] or chrom == "M":
        if coding:
            track = HG38COSMIC_CODING
            track_index = ".".join([HG38COSMIC_CODING, "tbi"])
        else:
            track = HG38COSMIC_NON_CODING
            track_index = ".".join([HG38COSMIC_NON_CODING, "tbi"])
    else:
        if coding:
            track = HG19COSMIC_CODING
            track_index = ".".join([HG19COSMIC_CODING, "tbi"])
        else:
            track = HG19COSMIC_NON_CODING
            track_index = ".".join([HG19COSMIC_NON_CODING, "tbi"])

    # if track file is contained in a bucket folder
    cloud_credentials = _get_cloud_credentials()
    cloud_folder = cloud_credentials.get("FOLDER_NAME")

    if cloud_folder is not None:
        cosmic_track["url"] = amazon_s3_url( cloud_credentials , "/".join([ cloud_folder, track ]))
        cosmic_track["indexURL"] = amazon_s3_url( cloud_credentials, "/".join([ cloud_folder, track_index ]))
    else:
        cosmic_track["url"] = amazon_s3_url(cloud_credentials, track)
        cosmic_track["indexURL"] = amazon_s3_url(cloud_credentials, track_index)

    return cosmic_track


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
