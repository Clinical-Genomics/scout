import logging
from typing import Optional

import cyvcf2

from scout.constants import CALLERS

LOG = logging.getLogger(__name__)

PASS_STATUS = "Pass"
FILTERED_STATUS = "Filtered"


def parse_callers(variant: cyvcf2.Variant, category: str = "snv") -> dict:
    """Parse how the different variant callers have performed

    Caller information can be passed in one of three ways, in order of priority:
    1. If a FOUND_IN tag (comma separated) is found, callers listed will be marked Pass
    2. If a svdb_origin tag (pipe separated) is found, callers listed will be marked Pass
    3. If a set tag (dash separated, GATK CombineVariants) is found, callers will be marked Pass or Filtered accordingly

    If the FILTER status is not PASS (e.g. None - cyvcf2 FILTER is None if VCF file column FILTER is "PASS"),
    in all of these cases, if a single caller is found, the caller status is set to the filter status.
    If there is more than one caller, we can't quite tell which one is which, so all caller statuses will be "Filtered" instead.

    Args:
        variant (cyvcf2.Variant): A variant object

    Returns:
        callers (dict): A dictionary on the format
        {'gatk': <filter>,'freebayes': <filter>,'samtools': <filter>}
    """
    FILTERED = "Filtered - {}"

    relevant_callers = CALLERS[category]
    callers = {caller["id"]: None for caller in relevant_callers}
    callers_keys = set(callers.keys())

    def get_callers_from_found_in(info_found_in: str, filter_status: Optional[str]) -> dict:
        """If a FOUND_IN tag (comma separated) is found, callers listed will be marked Pass.
        In case of a FILTER status, also set the caller status for a single caller to 'Filtered - status'.
        If more than one caller, and FILTER status, we cant really tell which said what, and all will be
        "Filtered".
        """
        found_ins: list = info_found_in.split(",")

        call_status = PASS_STATUS
        if filter_status is not None:
            call_status = (
                FILTERED.format(filter_status.replace(";", " - "))
                if len(found_ins) == 1
                else FILTERED_STATUS
            )

        for found_in in found_ins:
            called_by = found_in.split("|")[0]
            if called_by in callers_keys:
                callers[called_by] = call_status
        return callers

    info_found_in: str = variant.INFO.get("FOUND_IN")
    if info_found_in:
        return get_callers_from_found_in(info_found_in, variant.FILTER)

    def get_callers_from_svdb_origin(svdb_origin: str, filter_status: Optional[str]) -> dict:
        """If a svdb_origin tag (pipe separated) is found, callers listed will be marked Pass.
        In case of a FILTER status, also set the caller status for a single caller to 'Filtered - status'.
        """
        svdb_callers: list = svdb_origin.split("|")

        call_status = PASS_STATUS
        if filter_status is not None:
            call_status = (
                FILTERED.format(filter_status.replace(";", " - "))
                if len(svdb_callers) == 1
                else FILTERED_STATUS
            )

        for called_by in svdb_callers:
            if called_by in callers_keys:
                callers[called_by] = call_status
        return callers

    svdb_origin = variant.INFO.get("svdb_origin")
    if svdb_origin:
        return get_callers_from_svdb_origin(svdb_origin, variant.FILTER)

    def get_callers_from_set(info_set: str, filter_status: str) -> dict:
        """
        If the FILTER status is not PASS (e.g. None - cyvcf2 FILTER is None if VCF file column FILTER is "PASS"),
        in all of these cases, if a single caller is found, the "Pass" status is replaced with variant filter
            status. If there is more than one caller, we can't quite tell which one is which, so all will be "Filtered"
            without explicit status instead.

        """

        calls = info_set.split("-")

        call_status = PASS_STATUS
        if filter_status is not None:
            call_status = (
                FILTERED.format(filter_status.replace(";", " - "))
                if len(calls) == 1
                else FILTERED_STATUS
            )

        for call in calls:
            if call == "FilteredInAll":
                for caller in callers:
                    callers[caller] = FILTERED_STATUS
                return callers
            if call == "Intersection":
                for caller in callers:
                    callers[caller] = PASS_STATUS
                return callers
            if "filterIn" in call:
                if "Filtered" not in call_status:
                    call_status = FILTERED_STATUS
                for caller in callers:
                    if caller in call:
                        callers[caller] = call_status
            elif call in callers_keys:
                callers[call] = PASS_STATUS
        return callers

    info_set = variant.INFO.get("set")
    if info_set:
        return get_callers_from_set(info_set, variant.FILTER)

    def get_callers_gatk_snv_fallback(filter_status: Optional[str]):
        """As a final fallback, to accommodate a version range of MIP where no SNV caller was set for GATK,
        if this is an SNV variant, and no other call was found, set as if it was a GATK call with Pass or filter status.
        """
        filter_status_default = "Pass"
        if filter_status is not None:
            filter_status_default = FILTERED.format(filter_status.replace(";", " - "))
        callers["gatk"] = filter_status_default
        return callers

    if category == "snv":
        return get_callers_gatk_snv_fallback(variant.FILTER)

    return callers
