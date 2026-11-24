import logging
from typing import Optional, Tuple
from urllib.parse import unquote

from scout.constants import PROTEIN_HGVS_CONSEQUENCES, REPRESENTATIVE_TRANSCRIPT_PRIORITY

from .scout_requests import get_request_json

LOG = logging.getLogger(__name__)
VALIDATOR_URL = "https://rest.variantvalidator.org/VariantValidator/variantvalidator/{}/{}/select?content-type=application%2Fjson"


def validate_hgvs(build: str, desc: str) -> bool:
    """Validates a simple hgvs descriptor using the VariantValidator API (https://rest.variantvalidator.org/)

    Args:
        build(str): '37' or '38'
        desc(str): variant descriptor. Example: 'NC_000007.14:g.124851918C>A'

    Returns:
        validated(bool)
    """
    build = "GRCh37" if "37" in build else "GRCh38"
    validated = False
    url = VALIDATOR_URL.format(build, desc)
    try:
        res = get_request_json(url)
        validated = res["content"]["flag"] == "gene_variant"
    except Exception as ex:  # WHEN validation fails res["content"]["flag"] == "warning"
        LOG.warning(ex)

    return validated


def _transcript_priority(transcript: dict) -> Tuple[int, str]:
    """Return the selection priority (lower is better) and the reason for a transcript."""
    return next(
        (
            (rank, reason)
            for rank, (key, reason) in enumerate(REPRESENTATIVE_TRANSCRIPT_PRIORITY)
            if transcript.get(key)
        ),
        (
            len(REPRESENTATIVE_TRANSCRIPT_PRIORITY),
            "First annotated transcript",
        ),
    )


def get_representative_transcript(gene: dict) -> Optional[dict]:
    """Pick the transcript to represent a variant gene in brief displays, links and reports.

    Priority: gene panel disease associated, MANE Select, MANE Plus Clinical, HGNC primary,
    VEP canonical, any with a RefSeq identifier, first annotated transcript.
    MANE and RefSeq information are only present after the gene has been decorated with
    information from the hgnc_genes collection or if annotated by VEP.

    Args:
        gene: a variant gene, with its "transcripts"

    Returns:
        the selected transcript, or None if the gene has no transcripts
    """
    transcripts = gene.get("transcripts") or []
    if not transcripts:
        return None
    return min(transcripts, key=lambda transcript: _transcript_priority(transcript)[0])


def get_hgvs_reference(transcript: dict) -> Optional[str]:
    """Return the transcript accession that the transcript HGVS c. and p. are valid for.

    HGVS from VEP is computed on the annotated transcript. A MANE RefSeq accession is only used
    in place of an Ensembl transcript id since MANE pairs are guaranteed to be identical.
    Other RefSeq transcripts matched to an Ensembl transcript may differ in sequence, and are not
    used as HGVS reference.
    """
    return (
        transcript.get("mane_select_transcript")
        or transcript.get("mane_plus_clinical_transcript")
        or transcript.get("transcript_id")
    )


def get_brief_hgvs(transcript: dict) -> Optional[str]:
    """Return the most informative brief HGVS for a transcript: protein change (p.) for protein
    altering consequences, otherwise coding (c.). Falls back to whichever one is available.
    """
    hgvs_c = unquote(transcript.get("coding_sequence_name") or "") or None
    hgvs_p = unquote(transcript.get("protein_sequence_name") or "") or None

    consequences = set(transcript.get("functional_annotations") or [])
    if hgvs_p and consequences & PROTEIN_HGVS_CONSEQUENCES:
        return hgvs_p
    return hgvs_c or hgvs_p


def transcript_hgvs(transcript: dict) -> dict:
    """Summarise HGVS information for a (representative) transcript, for display.

    Returns:
        dict with the transcript ids, the selection reason, exon/intron, HGVS c./p.,
        a full "reference:c." HGVS descriptor and a brief c. or p. HGVS for compact displays
    """
    reference = get_hgvs_reference(transcript)
    hgvs_c = unquote(transcript.get("coding_sequence_name") or "") or None
    hgvs_p = unquote(transcript.get("protein_sequence_name") or "") or None

    return {
        "transcript_id": transcript.get("transcript_id"),
        "refseq_id": transcript.get("refseq_id"),
        "mane_select": transcript.get("mane_select_transcript"),
        "mane_plus_clinical": transcript.get("mane_plus_clinical_transcript"),
        "selection_reason": _transcript_priority(transcript)[1],
        "exon": transcript.get("exon"),
        "intron": transcript.get("intron"),
        "hgvs_reference": reference,
        "hgvs_c": hgvs_c,
        "hgvs_p": hgvs_p,
        "hgvs_c_full": f"{reference}:{hgvs_c}" if reference and hgvs_c else None,
        "hgvs_brief": get_brief_hgvs(transcript),
    }
