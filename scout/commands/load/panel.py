# -*- coding: utf-8 -*-
import logging

from pprint import pprint as pp

import click

from scout.parse.panel import get_panel_info
from scout.utils.handle import get_file_handle
from scout.utils.requests import fetch_mim_files
from scout.utils.date import get_date

from scout.parse.panel import parse_gene_panel, get_omim_panel_genes
from scout.build import build_panel


from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)


@click.command('panel', short_help='Load a gene panel')
@click.argument('path', 
    type=click.Path(exists=True), 
    required=False
)
@click.option('--panel-id', 
    help="The panel identifier name",
)
@click.option('--institute',
    help="Specify the owner of the panel. Defaults to cust000."
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
@click.option('--omim',
    is_flag=True,
    help="Load the OMIM-AUTO panel into scout. A OMIM api key is required to do this(https://omim.org/api)."
)
@click.option('--api-key',
    help="A OMIM api key, see https://omim.org/api."
)
@click.pass_context
def panel(context, date, display_name, version, panel_type, panel_id, path, institute, omim, api_key):
    """Add a gene panel to the database."""

    adapter = context.obj['adapter']
    institute = institute or 'cust000'
    if not path:
        if not omim:
            LOG.warning("Please provide a gene panel file or specify omim")
            context.abort()

    if omim:
        api_key = api_key or context.obj.get('omim_api_key')
        if not api_key:
            LOG.warning("Please provide a omim api key to load the omim gene panel")
            context.abort()
        #Check if OMIM-AUTO exists
        if adapter.gene_panel(panel_id='OMIM-AUTO'):
            LOG.warning("OMIM-AUTO already exists in database")
            LOG.info("To create a new version use scout update omim")
            return

        # Here we know that there is no panel loaded
        try:
            adapter.load_omim_panel(api_key, institute=institute)
        except Exception as err:
            LOG.error(err)
            context.abort()

        return

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
