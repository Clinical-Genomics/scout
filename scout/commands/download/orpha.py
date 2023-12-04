"""Code for handling downloading of orphadata files used by scout from CLI"""

import logging
import pathlib

import click

from scout.utils.scout_requests import fetch_orpha_files

LOG = logging.getLogger(__name__)


def print_orpha(out_dir):
    """writes orpha files to a directory

    Args:
        out_dir(Path)
    """
    orpha_files = fetch_orpha_files(product6=True)
    file_name = "orphadata_en_product6.xml"
    file_path = out_dir / file_name
    LOG.info(f"Print Orphadata to {file_path}")
    with file_path.open("w", encoding="utf-8") as outfile:
        for line in orpha_files["orphadata_en_product6"]:
            outfile.write(line + "\n")


@click.command("orpha", help="Download files from Orphadata")
@click.option("-o", "--out-dir", default="./", show_default=True)
def orpha(out_dir):
    """Download the ORPHA codes annotated with genes"""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    LOG.info(f"Download ORPHA resources to {out_dir}")

    print_orpha(out_dir)