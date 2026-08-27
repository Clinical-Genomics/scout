import logging
import pathlib

import click

from scout.commands.utils import outdir_option
from scout.utils.scout_requests import fetch_clingen_disease, fetch_clingen_dosage

LOG = logging.getLogger(__name__)

CLINGEN_FILES = {
    "disease": {
        "desc": "ClinGen Gene-Disease Validity Curations",
        "file_name": "clingen-gene-disease-summary.csv",
    },
    "dosage": {
        "desc": "ClinGen Dosage Sensitivity Curations",
        "file_name": "clingen-dosage-sensitivity.csv",
    },
}


def print_clingen(out_dir: str, clingen_info: dict) -> None:
    """Download ClinGen dosage sensitivity (regions and genes) and disease-gene files."""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    LOG.info("Download ClinGen resources to %s", out_dir)

    for clingen_key, clingen_file in CLINGEN_FILES.items():
        file_name = clingen_file["file_name"]
        file_path = out_dir / file_name
        LOG.info("Download %s ClinGen file to %s", clingen_file["desc"], file_path)
        with file_path.open("w", encoding="utf-8") as outfile:
            for line in clingen_info[clingen_key]:
                outfile.write(line + "\n")


@click.command("clingen", help="Download ClinGen files")
@outdir_option
def clingen(out_dir: str) -> None:
    """Download ClinGen dosage sensitivity (regions and genes) and disease-gene files."""

    clingen_info = {
        "dosage": fetch_clingen_dosage(),
        "disease": fetch_clingen_disease(),
    }

    print_clingen(out_dir, clingen_info)
