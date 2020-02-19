"""Code for handling downloading of HPO files used by scout from CLI"""
import logging
import pathlib

import click

from scout.utils.scout_requests import (fetch_hpo_genes,
                                        fetch_hpo_phenotype_to_terms,
                                        fetch_hpo_terms, fetch_hpo_to_genes)

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

    hpo_file_name = "ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype.txt"
    hpo_file_path = out_dir / hpo_file_name
    LOG.info("Download HPO genes to %s", hpo_file_path)
    with hpo_file_path.open("w", encoding="utf-8") as outfile:
        for line in fetch_hpo_genes():
            outfile.write(line + "\n")

    hpo_file_name = "ALL_SOURCES_ALL_FREQUENCIES_phenotype_to_genes.txt"
    hpo_file_path = out_dir / hpo_file_name
    LOG.info("Download HPO TO genes to %s", hpo_file_path)
    with hpo_file_path.open("w", encoding="utf-8") as outfile:
        for line in fetch_hpo_to_genes():
            outfile.write(line + "\n")

    hpo_file_name = "ALL_SOURCES_ALL_FREQUENCIES_diseases_to_genes_to_phenotypes.txt"
    hpo_file_path = out_dir / hpo_file_name
    LOG.info("Download HPO disease %s", hpo_file_path)
    with hpo_file_path.open("w", encoding="utf-8") as outfile:
        for line in fetch_hpo_phenotype_to_terms():
            outfile.write(line + "\n")


@click.command("hpo", help="Download hpo files")
@click.option("-o", "--out-dir", default="./", show_default=True)
def hpo(out_dir):
    """Download all files necessary for HPO"""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    LOG.info("Download HPO resources to %s", out_dir)

    print_hpo(out_dir)
