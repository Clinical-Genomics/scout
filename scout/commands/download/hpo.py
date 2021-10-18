"""Code for handling downloading of HPO files used by scout from CLI"""
import logging
import pathlib

import click

from scout.utils.scout_requests import fetch_hpo_files

LOG = logging.getLogger(__name__)


def print_hpo(out_dir, hpo_info):
    """Print HPO files to a directory

    Args:
        out_dir(Path)
        hpo_info(dict)
    """
    hpo_file_name = "hpo.obo"
    hpo_file_path = out_dir / hpo_file_name
    LOG.info("Download HPO terms to %s", hpo_file_path)
    with hpo_file_path.open("w", encoding="utf-8") as outfile:
        for line in hpo_info["hpo_terms"]:
            outfile.write(line + "\n")

    hpo_file_name = "genes_to_phenotype.txt"
    hpo_file_path = out_dir / hpo_file_name
    LOG.info("Download HPO genes to %s", hpo_file_path)
    with hpo_file_path.open("w", encoding="utf-8") as outfile:
        for line in hpo_info["genes_to_phenotype"]:
            outfile.write(line + "\n")

    hpo_file_name = "phenotype_to_genes.txt"
    hpo_file_path = out_dir / hpo_file_name
    LOG.info("Download HPO to genes to diagnosis data to %s", hpo_file_path)
    with hpo_file_path.open("w", encoding="utf-8") as outfile:
        for line in hpo_info["phenotype_to_genes"]:
            outfile.write(line + "\n")


@click.command("hpo", help="Download hpo files")
@click.option("-o", "--out-dir", default="./", show_default=True)
@click.option("--terms", is_flag=True, help="If only terms should be fetched and printed")
@click.option("--genes", is_flag=True, help="If only genes should be fetched and printed")
@click.option("--disease", is_flag=True, help="If only disease should be fetched and printed")
def hpo(out_dir, terms, genes, disease):
    """Download all files necessary for HPO

    If terms or genes or disease is used print this to terminal
    """

    kwargs = {"genes_to_phenotype": True, "phenotype_to_genes": True, "hpo_terms": True}
    if terms or genes or disease:
        kwargs = {
            "genes_to_phenotype": genes,
            "phenotype_to_genes": disease,
            "hpo_terms": terms,
        }
        hpo_info = fetch_hpo_files(**kwargs)
        if terms:
            info = hpo_info["hpo_terms"]
        elif genes:
            info = hpo_info["genes_to_phenotype"]
        else:
            info = hpo_info["phenotype_to_genes"]
        for line in info:
            click.echo(line)
        return

    hpo_info = fetch_hpo_files(**kwargs)
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    LOG.info("Download HPO resources to %s", out_dir)

    print_hpo(out_dir, hpo_info)
