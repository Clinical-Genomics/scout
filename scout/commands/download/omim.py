"""Code for handling downloading of HPO files used by scout from CLI"""
import logging
import pathlib

import click

from scout.utils.scout_requests import fetch_mim_files

LOG = logging.getLogger(__name__)


def print_omim(out_dir, api_key):
    """Print HPO files to a directory

    Args:
        out_dir(Path)
    """
    mim_files = fetch_mim_files(api_key, mim2genes=True, genemap2=True)
    file_name = "genemap2.txt"
    file_path = out_dir / file_name
    LOG.info("Print genemap genes to %s", file_path)
    with file_path.open("w", encoding="utf-8") as outfile:
        for line in mim_files["genemap2"]:
            outfile.write(line + "\n")

    file_name = "mim2genes.txt"
    file_path = out_dir / file_name
    LOG.info("Print mim2gene info to %s", file_path)
    with file_path.open("w", encoding="utf-8") as outfile:
        for line in mim_files["mim2genes"]:
            outfile.write(line + "\n")


@click.command("omim", help="Download a files with OMIM info")
@click.option("--api-key", help="Specify the api key", required=True)
@click.option("-o", "--out-dir", default="./", show_default=True)
def omim(out_dir, api_key):
    """Download the OMIM genes"""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    LOG.info("Download OMIM resources to %s", out_dir)

    print_omim(out_dir, api_key)
