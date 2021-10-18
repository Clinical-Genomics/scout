"""Code for handling downloading of ensembl files used by scout from CLI"""
import logging
import pathlib

import click

from scout.utils.scout_requests import (
    fetch_ensembl_exons,
    fetch_ensembl_genes,
    fetch_ensembl_transcripts,
)

LOG = logging.getLogger(__name__)


def print_ensembl(out_dir, resource_type, genome_build=None):
    """Fetch and print ensembl info to file

    If no genome build is used both builds will be fetched

    Args:
        out_dir(Path): Path to existing directory
        resource_type(str): in ['genes', 'transcripts', 'exons']
        genome_build

    """
    if resource_type not in ["genes", "transcripts", "exons"]:
        LOG.error("Invalid resource type")
        raise SyntaxError()

    builds = ["37", "38"]
    if genome_build:
        builds = [genome_build]

    LOG.info("Fetching ensembl %s, build: %s", resource_type, ",".join(builds))
    if resource_type == "genes":
        file_name = "ensembl_genes_{}.txt"
        fetch_function = fetch_ensembl_genes
    elif resource_type == "transcripts":
        file_name = "ensembl_transcripts_{}.txt"
        fetch_function = fetch_ensembl_transcripts
    else:
        file_name = "ensembl_exons_{}.txt"
        fetch_function = fetch_ensembl_exons

    for build in builds:
        file_path = out_dir / file_name.format(build)
        LOG.info("Print ensembl info %s to %s", build, file_path)
        with file_path.open("w", encoding="utf-8") as outfile:
            for line in fetch_function(build=build):
                outfile.write(line + "\n")
        LOG.info("Ensembl info saved")


@click.command("ensembl", help="Download files with ensembl info")
@click.option("-o", "--out-dir", default="./", show_default=True)
@click.option("--skip-tx", is_flag=True, help="Only download ensembl genes, skip transcripts")
@click.option("--exons", is_flag=True, help="If ensembl exons should be downloaded")
@click.option("--build", type=click.Choice(["37", "38"]), help="If only one build should be used")
def ensembl(out_dir, skip_tx, exons, build):
    """Download the Ensembl information"""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    LOG.info("Download ensembl results to %s", out_dir)

    print_ensembl(out_dir, "genes", build)

    if not skip_tx:
        print_ensembl(out_dir, "transcripts", build)

    if exons:
        print_ensembl(out_dir, "exons", build)
