# -*- coding: utf-8 -*-
import logging

from pprint import pprint as pp

import click

from scout.parse.panel import get_panel_info
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
@click.option('-v', '--version',type=float,)
@click.option('-t', '--panel-type', 
    default='clinical', 
    show_default=True,
    type=click.Choice(['clinical', 'research'])
)
@click.pass_context
def panel(context, date, display_name, version, panel_type, panel_id, path, institute):
    """Add a gene panel to the database."""
    adapter = context.obj['adapter']
    panel_lines = get_file_handle(path)
    
    try:
        panel_info = get_panel_info(
            panel_lines=panel_lines,
            panel_id=panel_id,
            institute=institute,
            version=version,
            date=date,
            display_name=display_name
            )
    except Exception as err:
        LOG.warning(err)
        context.abort()

    version = None
    if panel_info.get('version'):
        version = float(panel_info['version'])

    panel_id = panel_info['panel_id']
    display_name = panel_info['display_name'] or panel_id
    institute = panel_info['institute']
    date = panel_info['date']

    if not institute:
        LOG.warning("A Panel has to belong to a institute")
        context.abort()
    
    #Check if institute exists in database
    if not adapter.institute(institute):
        LOG.warning("Institute {0} does not exist in database".format(institute))
        context.abort()

    if not panel_id:
        LOG.warning("A Panel has to have a panel id")
        context.abort()
    
    if version:
        existing_panel = adapter.gene_panel(panel_id, version)
    else:
        existing_panel = adapter.gene_panel(panel_id)
        ## Assuming version 1.0
        version = 1.0

    if existing_panel:
        LOG.info("found existing panel")
        if version == existing_panel['version']:
            LOG.warning("Panel with same version exists in database")
            LOG.info("Reload with updated version")
            context.abort()
        display_name = display_name or existing_panel['display_name']
        institute = institute or existing_panel['institute']

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
