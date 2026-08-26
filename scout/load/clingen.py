from utils.scout_requests import fetch_clingen_dosage

from scout.parse.clingen import parse_clingen_dosage_csv


def load_clingen_dosage_sensitivity(adapter, dosage_lines):
    """Load the ClinGen dosage sensitivity information into the database.
    Also loads the ISCA regions information, as this is the primary source of ISCA regions.
    """

    if not dosage_lines:
        dosage_lines = fetch_clingen_dosage()

        hgnc_info, isca_info = parse_clingen_dosage_csv(dosage_lines)

        adapter.load_regions(isca_info)
