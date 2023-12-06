"""Code for handling downloading of files used by scout from CLI"""

import click

from .ensembl import ensembl as ensembl_command
from .everything import everything as everything_command
from .exac import exac as exac_command
from .hgnc import hgnc as hgnc_command
from .hpo import hpo as hpo_command
from .omim import omim as omim_command
from .orpha import orpha as orpha_command


@click.group()
def download():
    """
    Download resources used by scout
    """
    return


download.add_command(hpo_command)
download.add_command(hgnc_command)
download.add_command(ensembl_command)
download.add_command(exac_command)
download.add_command(omim_command)
download.add_command(orpha_command)
download.add_command(everything_command)
