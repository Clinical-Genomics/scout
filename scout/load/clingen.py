import logging

from scout.parse.clingen import parse_clingen_dosage_csv
from scout.utils.scout_requests import fetch_clingen_dosage

LOG = logging.getLogger(__name__)


def load_clingen_dosage_sensitivity(adapter, dosage_lines):
    """Load the ClinGen dosage sensitivity information into the database.
    Also loads the ISCA regions information, as this is the primary source of ISCA regions.
    """

    if not dosage_lines:
        LOG.info("Fetching ClinGen dosage sensitivity information from the remote URL.")
        dosage_lines = fetch_clingen_dosage()

    if not dosage_lines:
        raise ValueError("No ClinGen dosage sensitivity information found.")

    adapter.drop_regions()
    hgnc_info, isca_info = parse_clingen_dosage_csv(dosage_lines)

    adapter.load_regions(isca_info)
