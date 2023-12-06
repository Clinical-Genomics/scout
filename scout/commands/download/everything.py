"""Code for handling downloading Download all necessary resources for scout used by scout from
CLI
"""
import logging
import pathlib

import click

from .ensembl import ensembl
from .exac import exac
from .hgnc import hgnc
from .hpo import hpo
from .omim import omim
from .orpha import orpha

LOG = logging.getLogger(__name__)


@click.command("everything", help="Download all necessary resources for scout")
@click.option("--api-key", help="Specify the OMIM api key")
@click.option("-o", "--out-dir", default="./", show_default=True)
@click.option("--skip-tx", is_flag=True, help="Only download ensembl genes, skip transcripts")
@click.option("--exons", is_flag=True, help="If ensembl exons should be downloaded")
@click.option("--build", type=click.Choice(["37", "38"]), help="If only one build should be used")
@click.pass_context
def everything(ctx, out_dir, api_key, skip_tx, exons, build):
    """Download all necessary resources for scout"""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if api_key is None:
        LOG.warning("No OMIM api key provided, skipping OMIM")
    else:
        ctx.invoke(omim, out_dir=out_dir, api_key=api_key)
    ctx.invoke(orpha, out_dir=out_dir)
    ctx.invoke(hpo, out_dir=out_dir)
    ctx.invoke(exac, out_dir=out_dir)
    ctx.invoke(hgnc, out_dir=out_dir)
    ctx.invoke(ensembl, out_dir=out_dir, skip_tx=skip_tx, exons=exons, build=build)
