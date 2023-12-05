"""Code for handling downloading of orphadata files used by scout from CLI"""

import logging
import pathlib

import click

from scout.utils.scout_requests import fetch_orpha_files

LOG = logging.getLogger(__name__)


def print_orpha(out_dir: pathlib.Path) -> None:
    """Downloads orphadata product4 (Orphacodes mapped to HPO)
    and product6 (Orphacodes mapped to genes) and writes these as files in
    the specified directory
    """

    orpha_files = fetch_orpha_files(product4=True, product6=True)

    for key, contents in orpha_files.items():
        file_name = key + ".xml"
        file_path = out_dir / file_name
        LOG.info(f"Print Orphadata to {file_path}")
        with file_path.open("w", encoding="utf-8") as outfile:
            for line in orpha_files[key]:
                outfile.write(line + "\n")


@click.command("orpha", help="Download files from Orphadata")
@click.option("-o", "--out-dir", default="./", show_default=True)
def orpha(out_dir):
    """Download the ORPHA codes with gene and HPO annotations"""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    LOG.info(f"Download ORPHA resources to {out_dir}")

    print_orpha(out_dir)
