# -*- coding: utf-8 -*-
import logging

import click
from flask.cli import with_appcontext

from scout.parse.panel import parse_genes
from scout.server.extensions import store
from scout.utils.handle import get_file_handle

log = logging.getLogger(__name__)


@click.command("convert", short_help="Convert gene panels")
@click.argument("panel", type=click.File("r"))
@with_appcontext
def convert(panel):
    """Convert a gene panel with hgnc symbols to a new one with hgnc ids."""
    adapter = store
    new_header = [
        "hgnc_id",
        "hgnc_symbol",
        "disease_associated_transcripts",
        "reduced_penetrance",
        "genetic_disease_models",
        "mosaicism",
        "database_entry_version",
    ]

    genes = parse_genes(panel)

    adapter.add_hgnc_id(genes)

    click.echo("#{0}".format("\t".join(new_header)))
    for gene in genes:
        if gene.get("hgnc_id"):
            print_info = []
            for head in new_header:
                print_info.append(str(gene[head]) if gene.get(head) else "")

            click.echo("\t".join(print_info))
