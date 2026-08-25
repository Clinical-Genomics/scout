import logging
import pathlib

import click

from scout.commands.utils import outdir_option
from scout.utils.scout_requests import fetch_clingen_disease, fetch_clingen_dosage

LOG = logging.getLogger(__name__)

CLINGEN_FILES = [
    {"desc": "ClinGen Gene-Disease Validity Curations", "file_name": "ClinGen-Gene-Disease-Summary.csv", "info_key": "hpo_terms"},
    {
        "desc": "HPO genes to phenotype",
        "file_name": "genes_to_phenotype.txt",
        "info_key": "genes_to_phenotype",
    },


def print_clingen(out_dir: str, clingen_info: dict ) -> None:
    """Download ClinGen dosage sensitivity (regions and genes) and disease-gene files."""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    LOG.info("Download ClinGen resources to %s", out_dir)

    file_name = "hgnc.txt"
    file_path = out_dir / file_name
    LOG.info("Downloads ClinGen file to %s", file_path)
    with file_path.open("w", encoding="utf-8") as outfile:
        for line in fetch_hgnc():
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



