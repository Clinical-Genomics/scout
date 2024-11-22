import logging

from scout.constants import REV_CLINSIG_MAP

LOG = logging.getLogger(__name__)


def build_clnsig(clnsig_info: dict) -> dict:
    """Prepare clnsig information for database."""

    value = clnsig_info["value"]
    if value not in REV_CLINSIG_MAP:
        LOG.warning("Clinsig value %s does not have an internal representation", value)

    sign_number = REV_CLINSIG_MAP.get(value, 255)
    clnsig_obj = dict(
        value=sign_number,
        accession=clnsig_info.get("accession"),
        revstat=clnsig_info.get("revstat"),
    )

    if isinstance(value, str) and "low_penetrance" in value:
        clnsig_obj["low_penetrance"] = True

    return clnsig_obj
