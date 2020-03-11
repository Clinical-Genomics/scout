import logging
from scout.constants import REV_CLINSIG_MAP

LOG = logging.getLogger(__name__)


def build_clnsig(clnsig_info):
    """Prepare clnsig information for database

    Args:
        clnsig_info(dict): Parsed information from clinvar annotation

    Returns:
        clnsig_obj(dict): Converted and prepared for database
    """
    value = clnsig_info["value"]
    if value not in REV_CLINSIG_MAP:
        LOG.warning("Clinsig value %s does not have an internal representation", value)

    sign_number = REV_CLINSIG_MAP.get(value, 255)
    clnsig_obj = dict(
        value=sign_number,
        accession=clnsig_info.get("accession"),
        revstat=clnsig_info.get("revstat"),
    )

    return clnsig_obj
