# -*- coding: utf-8 -*-
import logging

from pprint import pprint as pp

import click

from scout.utils.date import get_date
from scout.utils.handle import get_file_handle

from scout.parse.panel import parse_gene_panel
from scout.build import build_panel

from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)


@click.command('panel', short_help='Load a gene panel')
@click.argument('path', type=click.Path(exists=True))
@click.option('--panel-id', 
    help="The panel identifier name",
)
@click.option('--institute',
    help="Specify the owner of the panel"
)
@click.option('-d', '--date', 
    help='date of gene panel on format 2017-12-24, default is today.'
)
@click.option('-n', '--display-name', 
    help='display name for the panel, optional'
)
@click.option('-v', '--version',
    type=float,
    default=1.0,
    show_default=True,
)
@click.option('-t', '--panel-type', 
    default='clinical', 
    show_default=True,
    type=click.Choice(['clinical', 'research'])
)
@click.pass_context
def panel(context, date, display_name, version, panel_type, panel_id, path, institute):
    """Add a gene panel to the database."""
    adapter = context.obj['adapter']
    f = get_file_handle(path)
    for line in f:
        line = line.rstrip()
        if line.startswith('##'):
            info = line[2:].split('=')
            field = info[0]
            value = info[1]
            if field == 'panel_id':
                panel_id = value
            elif field == 'institute':
                institute = value
            elif field == 'version':
                version = float(value)
            elif field == 'date':
                date = value
            elif name == 'display_name':
                display_name = value
    
    if version:
        existing_panel = adapter.gene_panel(panel_id, version)
    else:
        existing_panel = adapter.gene_panel(panel_id)

    if existing_panel:
        LOG.debug("found existing panel")
        display_name = display_name or existing_panel.display_name or panel_id
        institute = institute or existing_panel.institute

    try:
        date = get_date(date)
    except ValueError as error:
        LOG.warning(error)
        context.abort()

    if not institute:
        LOG.warning("A Panel has to belong to a institute")
        context.abort()

    if not panel_id:
        LOG.warning("A Panel has to have a panel id")
        context.abort()
        
    
    try:
        adapter.load_panel(
            path=path, 
            institute=institute, 
            panel_id=panel_id, 
            date=date, 
            panel_type=panel_type, 
            version=version, 
            display_name=display_name
        )
    except Exception as err:
        LOG.warning(err)
        context.abort()
