# -*- coding: utf-8 -*-
import logging

import click

from scout.load import load_panel
from scout.utils.date import get_date
from scout.utils.handle import get_file_handle

log = logging.getLogger(__name__)


@click.command('panel', short_help='Load a gene panel')
@click.argument('path', type=click.Path(exists=True))
@click.option('-d', '--date', help='date of gene panel. Default is today.')
@click.option('-n', '--name', help='display name for the panel')
@click.option('-v', '--version', help='panel version', show_default=True,
              default=1.0)
@click.option('-t', '--panel-type', default='clinical', show_default=True)
@click.option('--panel-id')
@click.option('--institute')
@click.pass_context
def panel(context, date, name, version, panel_type, panel_id, path, institute):
    """Add a gene panel to the database."""
    f = get_file_handle(path)
    for line in f:
        line = line.rstrip()
        if line.startswith('##'):
            info = line[2:].split('=')
            name = info[0]
            value = info[1]
            if name == 'panel_id':
                panel_id = value
            elif name == 'institute':
                institute = value
            elif name == 'version':
                version = float(value)
            elif name == 'date':
                date = value
            elif name == 'display_name':
                name = value

    try:
        date = get_date(date)
    except ValueError as error:
        log.warning(error)
        context.abort()

    adapter = context.obj['adapter']
    existing_panel = adapter.gene_panel(panel_id)
    if existing_panel:
        log.debug("found existing panel")
        name = name or existing_panel.display_name or panel_id
        institute = institute or existing_panel.institute

    info = {
        'file': path,
        'institute': institute,
        'type': panel_type,
        'date': date,
        'version': version,
        'name': panel_id,
        'full_name': name,
    }

    load_panel(adapter=adapter, panel_info=info)
