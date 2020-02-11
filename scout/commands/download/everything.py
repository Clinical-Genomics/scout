"""Code for handling downloading Download all necessary resources for scout used by scout from
CLI
"""
import logging
import pathlib

import click

from .ensembl import print_ensembl
from .exac import print_exac
from .hgnc import print_hgnc
from .hpo import print_hpo
from .omim import print_omim

LOG = logging.getLogger(__name__)


@click.command("everything", help="Download all necessary resources for scout")
@click.option("--api-key", help="Specify the api key")
@click.option("-o", "--out-dir", default="./", show_default=True)
@click.option(
    "--skip-tx", is_flag=True, help="Only download ensembl genes, skip transcripts"
)
@click.option("--exons", is_flag=True, help="If ensembl exons should be downloaded")
@click.option(
    "--build", type=click.Choice(["37", "38"]), help="If only one build should be used"
)
def everything(out_dir, api_key, skip_tx, exons, build):
    """Download all necessary resources for scout"""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not api_key:
        LOG.warning("No OMIM api key provided, skipping OMIM")
    else:
        print_omim(out_dir, api_key)
    print_exac(out_dir)
    print_hpo(out_dir)
    print_hgnc(out_dir)

    print_ensembl(out_dir, "genes", build)

    if not skip_tx:
        print_ensembl(out_dir, "transcripts", build)

    if exons:
        print_ensembl(out_dir, "exons", build)
