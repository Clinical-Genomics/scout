"""Code for handling downloading of the ExAC genes file used by scout from CLI"""
import logging
import pathlib

import click

from scout.utils.scout_requests import fetch_exac_constraint

LOG = logging.getLogger(__name__)


def print_exac(out_dir):
    """Print ExAC file to a directory

    Args:
        out_dir(Path)
    """
    file_name = "fordist_cleaned_exac_r03_march16_z_pli_rec_null_data.txt"
    file_path = out_dir / file_name
    LOG.info("Download ExAC gene info to %s", file_path)
    with file_path.open("w", encoding="utf-8") as outfile:
        for line in fetch_exac_constraint():
            outfile.write(line + "\n")


@click.command("exac", help="Download a file with ExAC gene info")
@click.option("-o", "--out-dir", default="./", show_default=True)
def exac(out_dir):
    """Download a file with ExAC gene info"""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    LOG.info("Download ExAC gene info")

    print_exac(out_dir)
