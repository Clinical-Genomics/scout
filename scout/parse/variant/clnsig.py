import logging
from typing import Dict, List, Optional, Union

import cyvcf2

LOG = logging.getLogger(__name__)


def parse_clnsig_low_penetrance(sig_groups: List[str]) -> List[str]:
    """If 'low_penetrance' is among the clnsig terms of an array, the term gets appended to the term immediately before in the array."""
    result = []
    for sig in sig_groups:
        if sig == "low_penetrance" and result:
            result[-1] += f",{sig}"
        else:
            result.append(sig)
    return result


from typing import Dict, List, Optional, Union
import cyvcf2


def parse_clnsig(
    variant: cyvcf2.Variant, transcripts: Optional[List[Dict[str, Union[str, int]]]] = None
) -> List[Dict[str, Union[str, int]]]:
    """Parse and return ClinVar significance information."""

    def parse_transcripts(transcripts: List[Dict[str, Union[str, int]]]) -> List[Dict[str, str]]:
        """Extract ClinVar annotations from transcripts."""
        clnsig_values = {
            anno.lstrip("_")
            for t in transcripts
            for annotation in t.get("clnsig", [])
            for anno in annotation.split("/")
        }
        return [{"value": annotation} for annotation in clnsig_values]

    def parse_int_format(
        acc: Union[str, int], sig: str, revstat: str
    ) -> List[Dict[str, Union[str, int]]]:
        """Handle integer-based ClinVar annotations."""
        revstat_groups = (
            [rev.lstrip("_") for rev in revstat.replace("&", ",").split(",")] if revstat else []
        )
        sig_groups = [
            "_".join(term.split(" "))
            for significance in sig.replace("&", ",").split(",")
            for term in significance.lstrip("_").split("/")
        ]
        sig_groups = parse_clnsig_low_penetrance(sig_groups)
        return [
            {"value": sig_term, "accession": int(acc), "revstat": ",".join(revstat_groups)}
            for sig_term in sig_groups
        ]

    def parse_older_format(acc: str, sig: str, revstat: str) -> List[Dict[str, Union[str, int]]]:
        """Parse older ClinVar formats where data is separated by pipes (`|`)."""
        return [
            {"value": int(significance), "accession": accession, "revstat": revstat}
            for acc_group, sig_group, revstat_group in zip(
                acc.split("|"), sig.split("|"), revstat.split("|")
            )
            for accession, significance, revstat in zip(
                acc_group.split(","), sig_group.split(","), revstat_group.split(",")
            )
        ]

    transcripts = transcripts or []
    acc = variant.INFO.get("CLNACC", variant.INFO.get("CLNVID", ""))
    sig, revstat = (
        variant.INFO.get("CLNSIG", "").lower(),
        variant.INFO.get("CLNREVSTAT", "").lower(),
    )
    onc, onc_revstat, onccdn = (
        variant.INFO.get("ONC", "").lower(),
        variant.INFO.get("ONCREVSTAT", "").lower(),
        variant.INFO.get("ONCDN", "").lower(),
    )

    # Try parsing from transcripts if `acc` is empty
    if not acc and transcripts:
        if transcripts[0].get("clnsig"):
            return parse_transcripts(transcripts)
        acc = transcripts[0].get("clinvar_clnvid", acc)
        sig = transcripts[0].get("clinvar_clnsig", sig)
        revstat = transcripts[0].get("clinvar_revstat", revstat)

    # Parse integer-based ClinVar annotations
    if acc and (isinstance(acc, int) or acc.isdigit()):
        return parse_int_format(acc, sig, revstat)

    # Parse older ClinVar formats
    if acc:
        return parse_older_format(acc, sig, revstat)

    return []


def is_pathogenic(variant: cyvcf2.Variant):
    """Check if a variant has the clinical significance to be loaded

    We want to load all variants that are in any of the predefined categories regardless of rank
    scores etc.

    To avoid parsing much, we first quickly check if we have a string match to substrings in
    all relevant categories, that are somewhat rare in the CSQ strings in general. If not,
    we check more carefully.

    We include the old style numerical categories as well for backwards compatibility.

    Returns:
        bool: If variant should be loaded based on clinvar or not
    """

    quick_load_categories = {"pathogenic", "conflicting_"}

    # check if VEP-annotated field contains clinvar pathogenicity info
    vep_info = variant.INFO.get("CSQ")
    if vep_info:
        for category in quick_load_categories:
            if category in vep_info.lower():
                return True

    load_categories: set = {
        "pathogenic",
        "likely_pathogenic",
        "conflicting_classifications_of_pathogenicity",
        "conflicting_interpretations_of_pathogenicity",
        "conflicting_interpretations",
        4,
        5,
        8,
    }

    # Otherwise check if clinvar pathogenicity status is in INFO field
    clnsig_accessions = parse_clnsig(variant)

    for annotation in clnsig_accessions:
        clnsig = annotation["value"]
        if clnsig in load_categories:
            return True
    return False
