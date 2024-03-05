import logging

LOG = logging.getLogger(__name__)

BUILD_TRANSCRIPT_OPTIONAL_KEYS = [
    "protein_id",
    "sift_prediction",
    "polyphen_prediction",
    "swiss_prot",
    "pfam_domain",
    "prosite_profile",
    "smart_domain",
    "biotype",
    "functional_annotations",
    "region_annotations",
    "exon",
    "intron",
    "strand",
    "coding_sequence_name",
    "protein_sequence_name",
    "superdups_fracmatch",
    "mane_select_transcript",
    "mane_plus_clinical_transcript",
]


def build_transcript(transcript: dict) -> dict:
    """Build a transcript object

    These key/values represent the transcripts that are parsed from the VCF, not
    the transcript definitions that are collected from Ensembl.
    """

    # Transcripts has to have an id
    transcript_id = transcript["transcript_id"]
    transcript_obj = dict(transcript_id=transcript_id)

    # Transcripts has to belong to a gene
    transcript_obj["hgnc_id"] = transcript["hgnc_id"]

    for key in BUILD_TRANSCRIPT_OPTIONAL_KEYS:
        if transcript.get(key):
            transcript_obj[key] = transcript[key]

    transcript_obj["is_canonical"] = transcript.get("is_canonical", False)

    return transcript_obj
