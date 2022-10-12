import logging

from scout.constants import CALLERS

LOG = logging.getLogger(__name__)


def parse_callers(variant, category="snv"):
    """Parse how the different variant callers have performed

    Caller information can be passed in one of three ways, in order of priority:
    1. If a FOUND_IN tag (comma separated) is found, callers listed will be marked Pass
    2. If a svdb_origin tag (pipe separated) is found, callers listed will be marked Pass
    3. If a set tag (dash separated, GATK CombineVariants) is found, callers will be marked Pass or Filtered accordingly

    Args:
        variant (cyvcf2.Variant): A variant object

    Returns:
        callers (dict): A dictionary on the format
        {'gatk': <filter>,'freebayes': <filter>,'samtools': <filter>}
    """
    relevant_callers = CALLERS[category]
    callers = {caller["id"]: None for caller in relevant_callers}

    other_info = variant.INFO.get("FOUND_IN")
    svdb_origin = variant.INFO.get("svdb_origin")
    raw_info = variant.INFO.get("set")

    if other_info:
        for info in other_info.split(","):
            called_by = info.split("|")[0]
            callers[called_by] = "Pass"
    elif svdb_origin:
        for called_by in svdb_origin.split("|"):
            callers[called_by] = "Pass"
    elif raw_info:
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

    if raw_info or svdb_origin or other_info:
        return callers

    if category == "snv":
        # cyvcf2 FILTER is None if VCF file column FILTER is "PASS"
        filter_status = "Pass"
        if variant.FILTER is not None:
            filter_status = "Filtered - {}".format(filter_status.replace(";", " - "))
        callers["gatk"] = filter_status

    return callers
