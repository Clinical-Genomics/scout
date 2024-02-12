"""Code for handling downloading of the ExAC genes file used by scout from CLI"""
import logging
import pathlib

import click

from scout.constants import GNOMAD_CONSTRAINT_FILENAME
from scout.utils.scout_requests import fetch_constraint

LOG = logging.getLogger(__name__)


def print_constraint(out_dir):
    """Print GnomAD constraint file to a directory

    Args:
        out_dir(Path)
    """
    file_path = out_dir / GNOMAD_CONSTRAINT_FILENAME
    LOG.info("Download GnomAD constraint info to %s", file_path)
    with file_path.open("w", encoding="utf-8") as outfile:
        for line in fetch_constraint():
            outfile.write(line + "\n")


@click.command("exac", help="Download a file with ExAC/GnomAD constraint info")
@click.option("-o", "--out-dir", default="./", show_default=True)
def exac(out_dir):
    """Download a file with ExAC / GnomAD constraint info"""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    LOG.info("Download ExAC / GnomAD constraint info")

    print_constraint(out_dir)
