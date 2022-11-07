import logging

from .scout_requests import get_request_json

LOG = logging.getLogger(__name__)
VALIDATOR_URL = "https://rest.variantvalidator.org/VariantValidator/variantvalidator/{}/{}/select?content-type=application%2Fjson"


def validate_hgvs(build, desc):
    """Validates a simple hgvs descriptor using the VariantValidator API (https://rest.variantvalidator.org/)

    Args:
        build(str): '37' or '38'
        desc(str): variant descriptor. Example: 'NC_000007.14:g.124851918C>A'

    Returns:
        validated(bool)
    """
    build = "GRCh37" if "37" in build else "GRCh38"
    validated = False
    url = VALIDATOR_URL.format(build, desc)
    try:
        res = get_request_json(url)
        validated = res["content"]["flag"] == "gene_variant"
    except Exception as ex:  # WHEN validation fails res["content"]["flag"] == "warning"
        LOG.warning(ex)

    return validated
