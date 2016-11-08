# -*- coding: utf-8 -*-
import logging

import click

from scout.parse.panel import parse_gene_panel
from scout.build import build_panel
from scout.load import load_panel

log = logging.getLogger(__name__)


@click.command()
@click.option('-d', '--date', help='date of gene panel')
@click.option('-n', '--name', help='display name for the panel')
@click.option('-v', '--version', help='panel version', default=1.0)
@click.option('-t', '--type', default='clinical')
@click.argument('panel_id')
@click.argument('panel_path', type=click.Path(exists=True))
@click.pass_context
def panel(context, date, name, version, type, panel_id, panel_path):
    """Add a gene panel to the database."""
    adapter = context.obj['adapter']
    info = {
        'file': panel_path,
        'type': type,
        'date': date,
        'version': version,
        'name': panel_id,
        'full_name': name or panel_id
    }
    panel_data = parse_gene_panel(info)
    panel_obj = build_panel(panel_data)
    load_panel(adapter, panel_obj)
