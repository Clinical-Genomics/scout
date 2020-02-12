"""Code for handling downloading of HPO files used by scout from CLI"""
import logging
import pathlib

import click

from scout.utils.scout_requests import fetch_hgnc

LOG = logging.getLogger(__name__)


def print_hgnc(out_dir):
    """Print HPO files to a directory

    Args:
        out_dir(Path)
    """
    file_name = "hgnc.txt"
    file_path = out_dir / file_name
    LOG.info("Downloads HGNC genes to %s", file_path)
    with file_path.open("w", encoding="utf-8") as outfile:
        for line in fetch_hgnc():
            outfile.write(line + "\n")


@click.command("hgnc", help="Download a file with HGNC genes")
@click.option("-o", "--out-dir", default="./", show_default=True)
def hgnc(out_dir):
    """Download the HGNC genes"""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    LOG.info("Download HGNC gene info")

    print_hgnc(out_dir)
