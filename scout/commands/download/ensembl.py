"""Code for handling downloading of ensembl files used by scout from CLI"""
import logging
import pathlib

import click

from scout.utils.scout_requests import (fetch_ensembl_exons,
                                        fetch_ensembl_genes,
                                        fetch_ensembl_transcripts)

LOG = logging.getLogger(__name__)


def print_ensembl(file_name, out_dir, fetch_function, genome_build=None):
    """Fetch and print ensembl info to file"""
    builds = ["37", "38"]
    if genome_build:
        builds = [genome_build]

    for build in builds:
        file_path = out_dir / file_name.format(build)
        LOG.info("Print ensembl info %s to %s", build, file_path)
        with file_path.open("w", encoding="utf-8") as outfile:
            for line in fetch_function(build=build):
                outfile.write(line + "\n")
        LOG.info("Ensembl info printed")


def print_ensembl_genes(out_dir, build=None):
    """Print ensembl gene files to a directory

    Args:
        out_dir(Path)
        build(str): If only one build should be printed
    """
    file_name = "ensembl_genes_{}.txt"
    print_ensembl(file_name, out_dir, fetch_ensembl_genes, build)


def print_ensembl_transcripts(out_dir, build=None):
    """Print ensembl transcript files to a directory

    Args:
        out_dir(Path)
    """
    file_name = "ensembl_transcripts_{}.txt"
    print_ensembl(file_name, out_dir, fetch_ensembl_transcripts, build)


def print_ensembl_exons(out_dir, build=None):
    """Print ensembl exon files to a directory

    Args:
        out_dir(Path)
    """
    file_name = "ensembl_exons_{}.txt"
    print_ensembl(file_name, out_dir, fetch_ensembl_exons, build)


@click.command("ensembl", help="Download files with ensembl info")
@click.option("-o", "--out-dir", default="./", show_default=True)
@click.option(
    "--skip-tx", is_flag=True, help="If only ensembl genes should be downloaded"
)
@click.option("--exons", is_flag=True, help="If ensembl exons should be downloaded")
@click.option(
    "--build", type=click.Choice(["37", "38"]), help="If only one build should be used"
)
def ensembl(out_dir, skip_tx, exons, build):
    """Download the Ensembl information"""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print_ensembl_genes(out_dir, build)

    if not skip_tx:
        print_ensembl_transcripts(out_dir, build)

    if exons:
        print_ensembl_exons(out_dir, build)
