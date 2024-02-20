from typing import Optional

from scout.models.hgnc_map import HgncTranscript


def build_transcript(transcript_info, build="37"):
    """Build a hgnc_transcript object

    Args:
        transcript_info(dict): Transcript information

    Returns:
        transcript_obj(HgncTranscript)
        {
            transcript_id: str, required
            hgnc_id: int, required
            build: str, required
            refseq_id: str,
            chrom: str, required
            start: int, required
            end: int, required
            is_primary: bool
        }
    """
    try:
        transcript_id = transcript_info["ensembl_transcript_id"]
    except KeyError:
        raise KeyError("Transcript has to have ensembl id")

    build = build
    is_primary = transcript_info.get("is_primary", False)

    refseq_id = transcript_info.get("refseq_id")
    refseq_identifiers = transcript_info.get("refseq_identifiers")

    mane_select: Optional[str] = transcript_info.get("mane_select")
    mane_plus_clinical: Optional[str] = transcript_info.get("mane_plus_clinical")

    try:
        chrom = transcript_info["chrom"]
    except KeyError:
        raise KeyError("Transcript has to have a chromosome")

    try:
        start = int(transcript_info["transcript_start"])
    except KeyError:
        raise KeyError("Transcript has to have start")
    except TypeError:
        raise TypeError("Transcript start has to be integer")

    try:
        end = int(transcript_info["transcript_end"])
    except KeyError:
        raise KeyError("Transcript has to have end")
    except TypeError:
        raise TypeError("Transcript end has to be integer")

    try:
        hgnc_id = int(transcript_info["hgnc_id"])
    except KeyError:
        raise KeyError("Transcript has to have a hgnc id")
    except TypeError:
        raise TypeError("hgnc id has to be integer")

    transcript_obj = HgncTranscript(
        transcript_id=transcript_id,
        hgnc_id=hgnc_id,
        chrom=chrom,
        start=start,
        end=end,
        is_primary=is_primary,
        refseq_id=refseq_id,
        refseq_identifiers=refseq_identifiers,
        build=build,
        mane_select=mane_select,
        mane_plus_clinical=mane_plus_clinical,
    )
    # Remove unnessesary keys
    for key in list(transcript_obj):
        if transcript_obj[key] is None:
            transcript_obj.pop(key)

    return transcript_obj
