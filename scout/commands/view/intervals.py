import logging
import click

from flask.cli import with_appcontext
from scout.server.extensions import store
from scout.constants import (BUILDS, CHROMOSOMES)

LOG = logging.getLogger(__name__)


@click.command('intervals', short_help='Show how many intervals that exists for each chromosome')
@click.option('-b', '--build',
              default='37',
              type=click.Choice(BUILDS)
              )
@with_appcontext
def intervals(build):
    """Show all coding intervals in the database"""
    LOG.info("Running scout view index")
    adapter = store

    if adapter.hgnc_collection.find().count() == 0:
        LOG.error('There are no genes in database to calculate intervals')
        return
    elif adapter.hgnc_collection.find({'build':build}).count() == 0:
        LOG.error('No genes in database with build {}'.format(build))
        return
    intervals = adapter.get_coding_intervals(build)
    nr_intervals = 0
    longest = 0
    for chrom in CHROMOSOMES:
        for iv in intervals[chrom]:
            iv_len = iv.end - iv.begin
            if iv_len > longest:
                longest = iv_len
        int_nr = len(intervals.get(chrom, []))
        click.echo("{0}\t{1}".format(chrom, int_nr))
        nr_intervals += int_nr

    LOG.info("Total nr intervals:%s", nr_intervals)
    LOG.info("Total nr genes:%s", adapter.all_genes(build).count())
    LOG.info("Longest interval:%s", longest)
