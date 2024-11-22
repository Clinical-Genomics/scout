import logging

from scout.constants import CALLERS

LOG = logging.getLogger(__name__)


def parse_callers(variant, category="snv"):
    """Parse how the different variant callers have performed

    Caller information can be passed in one of three ways, in order of priority:
    1. If a FOUND_IN tag (comma separated) is found, callers listed will be marked Pass
    2. If a svdb_origin tag (pipe separated) is found, callers listed will be marked Pass
    3. If a set tag (dash separated, GATK CombineVariants) is found, callers will be marked Pass or Filtered accordingly

    If the FILTER status is not PASS (e.g. None - cyvcf2 FILTER is None if VCF file column FILTER is "PASS"),
    in all of these cases, if a single caller is found, the "Pass" status is replaced with variant filter
    status. If there is more than one caller, we can't quite tell which one is which, so all will be "Filtered" instead.

    As a final fallback, to accommodate a version range of MIP where no SNV caller was set for GATK,
    if this is an SNV variant, and no other call was found, set as if it was a GATK call with Pass or filter status.


    Args:
        variant (cyvcf2.Variant): A variant object

    Returns:
        callers (dict): A dictionary on the format
        {'gatk': <filter>,'freebayes': <filter>,'samtools': <filter>}
    """
    relevant_callers = CALLERS[category]
    callers = {caller["id"]: None for caller in relevant_callers}
    callers_keys = set(callers.keys())

    other_info = variant.INFO.get("FOUND_IN")
    svdb_origin = variant.INFO.get("svdb_origin")
    raw_info = variant.INFO.get("set")

    filter_status_default = "Pass"
    if variant.FILTER is not None:
        filter_status_default = "Filtered - {}".format(variant.FILTER.replace(";", " - "))

    if other_info:
        infos = other_info.split(",")
        if len(infos) > 1:
            filter_status_default = "Pass"
        for info in infos:
            called_by = info.split("|")[0]
            if called_by in callers_keys:
                callers[called_by] = filter_status_default
    elif svdb_origin:
        svdb_callers = svdb_origin.split("|")
        if len(svdb_callers) > 1:
            filter_status_default = "Pass"
        for called_by in svdb_callers:
            if called_by in callers_keys:
                callers[called_by] = filter_status_default
    elif raw_info:
        info = raw_info.split("-")
        for call in info:

            if call == "FilteredInAll":
                filter_status = "Filtered"
                for caller in callers:
                    callers[caller] = filter_status
            elif call == "Intersection":
                for caller in callers:
                    callers[caller] = filter_status_default
            elif "filterIn" in call:
                filter_status = filter_status_default
                if "Filtered" not in filter_status_default:
                    filter_status = "Filtered"
                for caller in callers:
                    if caller in call:
                        callers[caller] = filter_status

            elif call in callers_keys:
                callers[call] = filter_status_default

    if raw_info or svdb_origin or other_info:
        return callers

    if category == "snv":
        filter_status = "Pass"
        if variant.FILTER is not None:
            filter_status = "Filtered - {}".format(filter_status.replace(";", " - "))
        callers["gatk"] = filter_status

    return callers
