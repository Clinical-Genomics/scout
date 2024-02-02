"""Code for handling downloading of ensembl files used by scout from CLI"""
import logging
import pathlib
from typing import List, Optional

import click

from scout.utils.ensembl_biomart_clients import EnsemblBiomartHandler

LOG = logging.getLogger(__name__)


def print_ensembl(
    out_dir: pathlib.Path, resource_type: List[str], genome_build: Optional[str] = None
):
    """Fetch and print Ensembl info to file. If no genome build is passed as argument, both builds will be fetched."""

    if resource_type not in ["genes", "transcripts", "exons"]:
        LOG.error("Invalid resource type")
        raise SyntaxError()

    builds = ["37", "38"]
    if genome_build:
        builds = [genome_build]

    LOG.info("Fetching ensembl %s, build: %s", resource_type, ",".join(builds))

    for build in builds:
        ensembl_client = EnsemblBiomartHandler(build=build)

        file_name: str = f"ensembl_{resource_type}_{build}.txt"
        file_path = out_dir / file_name

        LOG.info("Print ensembl info %s to %s", build, file_path)

        with file_path.open("w", encoding="utf-8") as outfile:
            for line in ensembl_client.stream_resource(interval_type=resource_type):
                outfile.write(line + "\n")

        LOG.info(f"{file_name} file saved to disk")


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
