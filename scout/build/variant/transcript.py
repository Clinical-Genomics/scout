import logging

LOG = logging.getLogger(__name__)


def build_transcript(transcript, build="37"):
    """Build a transcript object

    These represents the transcripts that are parsed from the VCF, not
    the transcript definitions that are collected from ensembl.

        Args:
            transcript(dict): Parsed transcript information

        Returns:
            transcript_obj(dict)
    """

    # Transcripts has to have an id
    transcript_id = transcript["transcript_id"]
    transcript_obj = dict(transcript_id=transcript_id)

    # Transcripts has to belong to a gene
    transcript_obj["hgnc_id"] = transcript["hgnc_id"]

    if transcript.get("protein_id"):
        transcript_obj["protein_id"] = transcript["protein_id"]

    if transcript.get("sift_prediction"):
        transcript_obj["sift_prediction"] = transcript["sift_prediction"]

    if transcript.get("polyphen_prediction"):
        transcript_obj["polyphen_prediction"] = transcript["polyphen_prediction"]

    if transcript.get("swiss_prot"):
        transcript_obj["swiss_prot"] = transcript["swiss_prot"]

    if transcript.get("pfam_domain"):
        transcript_obj["pfam_domain"] = transcript.get("pfam_domain")

    if transcript.get("prosite_profile"):
        transcript_obj["prosite_profile"] = transcript.get("prosite_profile")

    if transcript.get("smart_domain"):
        transcript_obj["smart_domain"] = transcript.get("smart_domain")

    if transcript.get("biotype"):
        transcript_obj["biotype"] = transcript.get("biotype")

    if transcript.get("functional_annotations"):
        transcript_obj["functional_annotations"] = transcript["functional_annotations"]

    if transcript.get("region_annotations"):
        transcript_obj["region_annotations"] = transcript["region_annotations"]

    if transcript.get("exon"):
        transcript_obj["exon"] = transcript.get("exon")

    if transcript.get("intron"):
        transcript_obj["intron"] = transcript.get("intron")

    if transcript.get("strand"):
        transcript_obj["strand"] = transcript.get("strand")

    if transcript.get("coding_sequence_name"):
        transcript_obj["coding_sequence_name"] = transcript["coding_sequence_name"]

    if transcript.get("protein_sequence_name"):
        transcript_obj["protein_sequence_name"] = transcript["protein_sequence_name"]

    if transcript.get("superdups_fracmatch"):
        transcript_obj["superdups_fracmatch"] = transcript["superdups_fracmatch"]

    if transcript.get("mane_transcript"):
        transcript_obj["mane_transcript"] = transcript["mane_transcript"]

    transcript_obj["is_canonical"] = transcript.get("is_canonical", False)

    return transcript_obj
