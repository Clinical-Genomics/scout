"""Code for handling downloading of HPO files used by scout from CLI"""
import logging
from pathlib import Path
from typing import Dict

import click

from scout.utils.scout_requests import fetch_mim_files

LOG = logging.getLogger(__name__)


def print_omim(out_dir: Path, api_key: str) -> None:
    """writes OMIM files to a directory"""
    mim_files: Dict = fetch_mim_files(api_key, mim2genes=True, genemap2=True)
    file_name: str = "genemap2.txt"
    file_path: Path = out_dir / file_name
    LOG.info("Print genemap genes to %s", file_path)
    with file_path.open("w", encoding="utf-8") as outfile:
        for line in mim_files["genemap2"]:
            outfile.write(line + "\n")

    file_name: str = "mim2genes.txt"
    file_path: Path = out_dir / file_name
    LOG.info("Print mim2gene info to %s", file_path)
    with file_path.open("w", encoding="utf-8") as outfile:
        for line in mim_files["mim2genes"]:
            outfile.write(line + "\n")


@click.command("omim", help="Download a files with OMIM info")
@click.option("--api-key", help="Specify the api key", required=True)
@click.option("-o", "--out-dir", default="./", show_default=True)
def omim(out_dir: str, api_key: str) -> None:
    """Download the OMIM genes"""
    out_dir: Path = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    LOG.info("Download OMIM resources to %s", out_dir)

    print_omim(out_dir, api_key)
