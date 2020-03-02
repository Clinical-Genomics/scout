"""Code for handling downloading of HPO files used by scout from CLI"""
import logging
import pathlib

import click

from scout.utils.scout_requests import (fetch_hpo_terms, fetch_genes_to_hpo_to_disease, fetch_hpo_to_genes_to_disease)

LOG = logging.getLogger(__name__)


def print_hpo(out_dir):
    """Print HPO files to a directory

    Args:
        out_dir(Path)
    """
    hpo_file_name = "hpo.obo"
    hpo_file_path = out_dir / hpo_file_name
    LOG.info("Download HPO terms to %s", hpo_file_path)
    with hpo_file_path.open("w", encoding="utf-8") as outfile:
        for line in fetch_hpo_terms():
            outfile.write(line + "\n")

    hpo_file_name = "genes_to_phenotype.txt"
    hpo_file_path = out_dir / hpo_file_name
    LOG.info("Download HPO genes to %s", hpo_file_path)
    with hpo_file_path.open("w", encoding="utf-8") as outfile:
        for line in fetch_genes_to_hpo_to_disease():
            outfile.write(line + "\n")

    hpo_file_name = "phenotype_to_genes.txt"
    hpo_file_path = out_dir / hpo_file_name
    LOG.info("Download HPO to genes to diagnosis data to %s", hpo_file_path)
    with hpo_file_path.open("w", encoding="utf-8") as outfile:
        for line in fetch_hpo_to_genes_to_disease():
            outfile.write(line + "\n")


@click.command("hpo", help="Download hpo files")
@click.option("-o", "--out-dir", default="./", show_default=True)
def hpo(out_dir):
    """Download all files necessary for HPO"""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    LOG.info("Download HPO resources to %s", out_dir)

    print_hpo(out_dir)
