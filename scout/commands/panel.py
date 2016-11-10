# -*- coding: utf-8 -*-
import logging

import click

from scout.load import load_panel
from scout.utils.date import get_date

log = logging.getLogger(__name__)

@click.command()
@click.option('-d', '--date', 
    help='date of gene panel. Default is today.',
)
@click.option('-n', '--name', 
    help='display name for the panel'
)
@click.option('-v', '--version', 
    help='panel version', 
    default=1.0
)
@click.option('-t', '--type', 
    default='clinical'
)
@click.option('-i', '--institute', 
    required=True
)
@click.option('--panel-id',
    required = True
)
@click.option('--path', 
    required = True,
    type=click.Path(exists=True)
)
@click.pass_context
def panel(context, date, name, version, type, panel_id, path, institute):
    """Add a gene panel to the database."""
    date = get_date(date)
    
    adapter = context.obj['adapter']
    info = {
        'file': path,
        'type': type,
        'date': date,
        'version': version,
        'institute': institute,
        'name': panel_id,
        'full_name': name or panel_id
    }
    
    load_panel(
        adapter=adapter,
        panel_info=info
    )
