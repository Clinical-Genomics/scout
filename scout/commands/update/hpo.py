"""CLI to update hpo terms"""

import logging

import click
from flask.cli import with_appcontext

from scout.commands.utils import abort_if_false
from scout.load.hpo import load_hpo_terms
from scout.server.extensions import store
from scout.utils.handle import get_file_handle

LOG = logging.getLogger(__name__)


@click.command("hpo", short_help="Update hpo terms")
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Are you sure you want to drop the hpo terms?",
)
@click.option(
    "--hpoterms",
    type=click.Path(exists=True),
    help=("Path to file with HPO terms. This is the " "file called hpo.obo"),
)
@click.option(
    "--hpo-to-genes",
    type=click.Path(exists=True),
    help=(
        "Path to file with map from HPO terms to genes. This is the file called "
        "phenotype_to_genes.txt"
    ),
)
@with_appcontext
def hpo(hpoterms, hpo_to_genes):
    """
    Update the HPO terms in the database. Fetch the latest release and update terms.
    """
    LOG.info("Running Scout update HPO")
    adapter = store

    if hpoterms:
        hpoterms = get_file_handle(hpoterms)
    if hpo_to_genes:
        hpo_to_genes = get_file_handle(hpo_to_genes)

    load_hpo_terms(
        adapter,
        hpo_lines=hpoterms,
        hpo_gene_lines=hpo_to_genes,
    )
