# -*- coding: utf-8 -*-
import logging

import click
from mongoengine import connect
import yaml

from scout.ext.backend.mongo import MongoAdapter
from .add import add_case

log = logging.getLogger(__name__)


@click.group()
@click.option('-c', '--config', type=click.File('r'))
@click.option('-d', '--database')
@click.option('-u', '--username')
@click.option('-p', '--password')
@click.option('-o', '--port', default=27017)
@click.option('-h', '--host', default='localhost',
              help='can also be used as URI')
@click.pass_context
def base(context, config, database, username, password, port, host):
    """Scout CLI for interacting with the database."""
    context.obj = yaml.load(config) if config else {}
    context.obj['db'] = MongoAdapter()
    connect(
        database or context.obj.get('database', 'variantDatabase'),
        host=host or context.obj.get('host'),
        port=port or context.obj.get('port'),
        username=username or context.obj.get('username'),
        password=password or context.obj.get('password')
    )


@base.command()
@click.option('-s', '--sampleinfo', type=click.File('r'), required=True)
@click.option('-p', '--ped', type=click.File('r'), required=True,
              help="pedigree file for the family")
@click.option('-v', '--vcf', type=click.Path(exists=True), required=True,
              help="variant VCF file")
@click.option('-m', '--madeline', type=click.Path(exists=True))
@click.option('-t', '--variant-type', default='clinical',
              help="clinical or research variants")
@click.option('--variants', default=5000)
@click.option('--threshold', default=0)
@click.pass_context
def add(context, sampleinfo, ped, vcf, variant_type, madeline, variants,
        threshold):
    """Add a new case to the database."""
    sampleinfo_data = yaml.load(sampleinfo)
    add_case(context.obj['db'], sampleinfo_data, ped, vcf, variant_type,
             madeline_exe=madeline, variants=variants, threshold=threshold)


@base.command()
def delete():
    """Delete a case from the database."""
    pass
