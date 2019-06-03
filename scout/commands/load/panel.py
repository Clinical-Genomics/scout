# -*- coding: utf-8 -*-
import logging

from pprint import pprint as pp

import click
from flask.cli import with_appcontext, current_app
from scout.server.extensions import store

from scout.utils.requests import fetch_mim_files
from scout.utils.date import get_date

from scout.load.panel import (load_panel_app, load_panel)

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
@click.option('--panel-app',
    is_flag=True,
    help="Load all PanelApp panels into scout."
)
@with_appcontext
def panel(path, date, display_name, version, panel_type, panel_id, institute, omim, api_key, panel_app):
    """Add a gene panel to the database."""

    adapter = store
    institute = institute or 'cust000'

    if omim:
        api_key = api_key or current_app.config.get('OMIM_API_KEY')
        if not api_key:
            LOG.warning("Please provide a omim api key to load the omim gene panel")
            raise click.Abort()
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
            raise click.Abort()

    if panel_app:
        # try:
        load_panel_app(adapter, panel_id, institute=institute)
        # except Exception as err:
        #     LOG.warning(err)
        #     raise click.Abort()

    if (omim or panel_app):
        return

    if path is None:
        LOG.info("Please provide a panel")
        return
    try:
        load_panel(path, adapter, date, display_name, version, panel_type, panel_id, institute)
    except Exception as err:
        LOG.warning(err)
        raise click.Abort()
