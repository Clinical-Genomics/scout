import logging

from scout.constants import CALLERS

LOG = logging.getLogger(__name__)


def parse_callers(variant, category="snv"):
    """Parse how the different variant callers have performed

    Args:
        variant (cyvcf2.Variant): A variant object

    Returns:
        callers (dict): A dictionary on the format
        {'gatk': <filter>,'freebayes': <filter>,'samtools': <filter>}
    """
    relevant_callers = CALLERS[category]
    callers = {caller["id"]: None for caller in relevant_callers}
    raw_info = variant.INFO.get("set")
    if raw_info:
        info = raw_info.split("-")
        for call in info:
            if call == "FilteredInAll":
                for caller in callers:
                    callers[caller] = "Filtered"
            elif call == "Intersection":
                for caller in callers:
                    callers[caller] = "Pass"
            elif "filterIn" in call:
                for caller in callers:
                    if caller in call:
                        callers[caller] = "Filtered"

            elif call in set(callers.keys()):
                callers[call] = "Pass"
    # The following is parsing of a custom made merge
    other_info = variant.INFO.get("FOUND_IN")
    if other_info:
        for info in other_info.split(","):
            called_by = info.split("|")[0]
            callers[called_by] = "Pass"

    if category == "snv" and not raw_info or other_info:
        # cyvcf2 FILTER is None if VCF file column FILTER is "PASS"
        filter_status = "Pass"
        if variant.FILTER is not None:
            filter_status = "Filtered - {}".format(filter_status.replace(";", " - "))
        callers["gatk"] = filter_status

    return callers
