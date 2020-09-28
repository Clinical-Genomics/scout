import logging

LOG = logging.getLogger(__name__)


def parse_clnsig(variant, transcripts=None):
    """Get the clnsig information

    The clinvar format has changed several times and this function will try to parse all of them.
    The first format represented the clinical significance terms with numbers. This was then
    replaced by strings and the separator changed. At this stage the possibility to connect review
    stats to a certain significance term was taken away. So now we can only annotate each
    significance term with all review stats.
    Also the clinvar accession numbers are in some cases annotated with the info key CLNACC and
    sometimes with CLNVID.
    This function parses also Clinvar annotations performed by VEP (CSQ field, parsed transcripts required)

    Args:
        variant(cyvcf2.Variant)
        transcripts(iterable(dict))

    Returns:
        clnsig_accsessions(list(dict)): A list with clnsig accessions
    """
    transcripts = transcripts or []
    acc = variant.INFO.get("CLNACC", variant.INFO.get("CLNVID", ""))
    sig = variant.INFO.get("CLNSIG", "").lower()
    revstat = variant.INFO.get("CLNREVSTAT", "").lower()

    clnsig_accessions = []

    if acc == "" and transcripts:
        if transcripts[0].get("clnsig"):
            clnsig = set()
            for transcript in transcripts:
                for annotation in transcript.get("clnsig", []):
                    for anno in annotation.split("/"):
                        clnsig.add(anno.lstrip("_"))
            for annotation in clnsig:
                clnsig_accessions.append({"value": annotation})

            return clnsig_accessions

        # VEP 97+ annotated clinvar info:
        if transcripts[0].get("clinvar_clnvid"):
            acc = transcripts[0]["clinvar_clnvid"]
            sig = transcripts[0].get("clinvar_clnsig")
            revstat = transcripts[0].get("clinvar_revstat")

    # There are some versions where clinvar uses integers to represent terms
    if isinstance(acc, int) or acc.isdigit():
        revstat_groups = []
        if revstat:
            revstat_groups = [rev.lstrip("_") for rev in revstat.replace("&", ",").split(",")]

        sig_groups = []
        for significance in sig.replace("&", ",").split(","):
            for term in significance.lstrip("_").split("/"):
                sig_groups.append("_".join(term.split(" ")))

        for sig_term in sig_groups:
            clnsig_accession = {
                "value": sig_term,
                "accession": int(acc),
                "revstat": ",".join(revstat_groups),
            }
            clnsig_accessions.append(clnsig_accession)

    # Test to parse the older format
    if acc and not clnsig_accessions:
        acc_groups = acc.split("|")
        sig_groups = sig.split("|")
        revstat_groups = revstat.split("|")
        for acc_group, sig_group, revstat_group in zip(acc_groups, sig_groups, revstat_groups):
            accessions = acc_group.split(",")
            significances = sig_group.split(",")
            revstats = revstat_group.split(",")
            for accession, significance, revstat in zip(accessions, significances, revstats):
                clnsig_accessions.append(
                    {
                        "value": int(significance),
                        "accession": accession,
                        "revstat": revstat,
                    }
                )

    return clnsig_accessions


def is_pathogenic(variant):
    """Check if a variant has the clinical significance to be loaded

    We want to load all variants that are in any of the predefined categories regardless of rank
    scores etc.

    Args:
        variant(cyvcf2.Variant)

    Returns:
        bool: If variant should be loaded based on clinvar or not
    """

    load_categories = set(
        [
            "pathogenic",
            "likely_pathogenic",
            "conflicting_interpretations_of_pathogenicity",
            "conflicting_interpretations",
        ]
    )

    # check if VEP-annotated field contains clinvar pathogenicity info
    vep_info = variant.INFO.get("CSQ")
    if vep_info:
        for category in load_categories:
            if category in vep_info.lower():
                return True

    # Otherwise check if clinvar pathogenicity status is in INFO field
    clnsig_accessions = parse_clnsig(variant)

    for annotation in clnsig_accessions:
        clnsig = annotation["value"]
        if clnsig in load_categories:
            return True
        if isinstance(clnsig, int):
            if clnsig == 4 or clnsig == 5:
                return True

    return False
