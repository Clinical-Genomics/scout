from scout.models.hgnc_map import Exon


def build_exon(exon_info, build="37"):
    """Build a Exon object object

    Args:
        exon_info(dict): Exon information

    Returns:
        exon_obj(Exon)

    "exon_id": str, # str(chrom-start-end)
    "chrom": str,
    "start": int,
    "end": int,
    "transcript": str, # ENST ID
    "hgnc_id": int,      # HGNC_id
    "rank": int, # Order of exon in transcript
    "strand": int, # 1 or -1
    "build": str, # Genome build
    """
    try:
        ensembl_exon_id = exon_info["ens_exon_id"]
    except KeyError:
        raise KeyError("Exons has to have a ensembl_exon_id")

    try:
        chrom = str(exon_info["chrom"])
    except KeyError:
        raise KeyError("Exons has to have a chromosome")

    try:
        start = int(exon_info["start"])
    except KeyError:
        raise KeyError("Exon has to have a start")
    except TypeError:
        raise TypeError("Exon start has to be integer")

    try:
        end = int(exon_info["end"])
    except KeyError:
        raise KeyError("Exon has to have a end")
    except TypeError:
        raise TypeError("Exon end has to be integer")

    try:
        rank = int(exon_info["rank"])
    except KeyError:
        raise KeyError("Exon has to have a rank")
    except TypeError:
        raise TypeError("Exon rank has to be integer")

    try:
        strand = int(exon_info["strand"])
    except KeyError:
        raise KeyError("Exon has to have a strand")
    except TypeError:
        raise TypeError("Exon strand has to be integer")

    try:
        exon_id = exon_info["exon_id"]
    except KeyError:
        raise KeyError("Exons has to have a id")

    try:
        transcript = exon_info["transcript"]
    except KeyError:
        raise KeyError("Exons has to have a transcript")

    try:
        hgnc_id = int(exon_info["hgnc_id"])
    except KeyError:
        raise KeyError("Exons has to have a hgnc_id")
    except TypeError:
        raise TypeError("hgnc_id has to be integer")

    exon_obj = Exon(
        exon_id=exon_id,
        chrom=chrom,
        start=start,
        end=end,
        strand=strand,
        rank=rank,
        transcript=transcript,
        hgnc_id=hgnc_id,
        build=build,
    )

    return exon_obj
