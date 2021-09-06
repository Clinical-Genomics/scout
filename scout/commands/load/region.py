#!/usr/bin/env python
# encoding: utf-8
import logging

import click
from flask.cli import with_appcontext

from scout.load.all import load_region
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("region", short_help="Load variants from region")
@click.option("--hgnc-id", type=int, help="Use a existing hgnc id to define the region")
@click.option("--case-id", required=True, help="Id of case")
@click.option("-c", "--chromosome")
@click.option("-s", "--start", type=int)
@click.option("-e", "--end", type=int)
@with_appcontext
def region(hgnc_id, case_id, chromosome, start, end):
    """Load all variants in a region to a existing case"""
    adapter = store
    load_region(
        adapter=adapter,
        case_id=case_id,
        hgnc_id=hgnc_id,
        chrom=chromosome,
        start=start,
        end=end,
    )
