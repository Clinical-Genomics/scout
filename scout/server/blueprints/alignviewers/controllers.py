import logging
from flask import current_app

LOG = logging.getLogger(__name__)

# Genome reference tracks
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

# Gene tracks
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


# Clinvar tracks
HG38CLINVAR_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg38/bbi/clinvar/clinvarMain.bb"
HG19CLINVAR_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg19/bbi/clinvar/clinvarMain.bb"

HG38CLINVAR_CNVS_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg38/bbi/clinvar/clinvarCnv.bb"
HG19CLINVAR_CNVS_URL = "https://hgdownload.soe.ucsc.edu/gbdb/hg19/bbi/clinvar/clinvarCnv.bb"


def get_cloud_credentials():
    """Returns cloud S3 storage credentials as a dictionary

    Returns:
        cloud_credentials(list): [endpoint_url, access_key, secrey_access_key, bucket_name]

    """
    cloud_credentials = {
        "region": current_app.config.get("REGION_NAME"),
        "key": current_app.config.get("ACCESS_KEY"),
        "secret_key": current_app.config.get("SECRET_ACCESS_KEY"),
        "bucket": current_app.config.get("BUCKET_NAME"),
        "folder": current_app.config.get("BUCKET_FOLDER"),  # Could be None
    }
    LOG.debug(f"cloud_credentials--->{cloud_credentials}")
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

def cloud_track(track_obj):
    """Return a dictionary consisting in the cosmic coding track

    Accepts:
        track_obj(dict)
            Example: "cosmic_coding_v90_hg19": {
                "description" : "Cosmic coding mutations v90 hg19",
                "file_name": "CosmicCodingMuts_v90_hg19.vcf.gz",
                "type": "variant",
                "format": "vcf",
                "displayMode": "squished",
                "genome_build": "37",
                "access_type": "credentials",
                "index_format": "tbi"
            }

    Returns:
        igv_track(dict)

    """
    # if track file is contained in a bucket folder
    cloud_credentials = get_cloud_credentials()
    track_url = track_obj["file_name"]
    track_index = ".".join([track_url,track_obj["index_format"]])

    cloud_folder = cloud_credentials.get("folder")

    if cloud_folder is not None:
        track_url = "/".join([cloud_folder, track_url])
        track_index = "/".join([cloud_folder, track_index])

    igv_track = dict(
        name = track_obj.get("description", track_obj.get("file_name")),
        type = track_obj.get("type"),
        format = track_obj.get("format"),
        displayMode = track_obj.get("displayMode", "squished"),
        url = track_url,
        indexURL = track_index
    )
    return igv_track

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
