"""scout.load.panel.py

functions to load panels into the database

"""

import logging
import json

from pprint import pprint as pp

from scout.utils.handle import get_file_handle
from scout.parse.panel import (get_panel_info, parse_panel_app_panel, parse_gene_panel)
from scout.utils.requests import get_request

LOG = logging.getLogger(__name__)


def load_panel(panel_path, adapter, date=None, display_name=None, version=None, panel_type=None, 
               panel_id=None, institute=None):
    """Load a manually curated gene panel into scout
    
    Args:
        panel_path(str): path to gene panel file
        adapter(scout.adapter.MongoAdapter)
        date(str): date of gene panel on format 2017-12-24
        display_name(str)
        version(float)
        panel_type(str)
        panel_id(str)
        institute(str)
    
    """
    panel_lines = get_file_handle(panel_path)

    try:
        # This will parse panel metadata if includeed in panel file
        panel_info = get_panel_info(
            panel_lines=panel_lines,
            panel_id=panel_id,
            institute=institute,
            version=version,
            date=date,
            display_name=display_name
            )
    except Exception as err:
        raise err

    version = None
    if panel_info.get('version'):
        version = float(panel_info['version'])

    panel_id = panel_info['panel_id']
    display_name = panel_info['display_name'] or panel_id
    institute = panel_info['institute']
    date = panel_info['date']

    if not institute:
        raise SyntaxError("A Panel has to belong to a institute")

    #Check if institute exists in database
    if not adapter.institute(institute):
        raise SyntaxError("Institute {0} does not exist in database".format(institute))

    if not panel_id:
        raise SyntaxError("A Panel has to have a panel id")
    
    if version:
        existing_panel = adapter.gene_panel(panel_id, version)
    else:
        ## Assuming version 1.0
        existing_panel = adapter.gene_panel(panel_id)
        version = 1.0
        LOG.info("Set version to %s", version)

    if existing_panel:
        LOG.info("found existing panel")
        if version == existing_panel['version']:
            LOG.warning("Panel with same version exists in database")
            LOG.info("Reload with updated version")
            raise SyntaxError()
        display_name = display_name or existing_panel['display_name']
        institute = institute or existing_panel['institute']
    
    parsed_panel = parse_gene_panel(
        path=panel_path,
        institute=institute,
        panel_type=panel_type,
        date=date,
        version=version,
        panel_id=panel_id,
        display_name=display_name,
    )
    
    try:
        adapter.load_panel(parsed_panel=parsed_panel)
    except Exception as err:
        raise err

def load_panel_app(adapter, panel_id=None, institute='cust000'):
    """Load PanelApp panels into scout database
    
    If no panel_id load all PanelApp panels 
    
    Args:
        adapter(scout.adapter.MongoAdapter)
        panel_id(str): The panel app panel id
    """
    base_url = 'https://panelapp.genomicsengland.co.uk/WebServices/{0}/'
    
    hgnc_map = adapter.genes_by_alias()
    
    if panel_id:
        panel_ids = [panel_id]

    if not panel_id:
        
        LOG.info("Fetching all panel app panels")
        data = get_request(base_url.format('list_panels'))
    
        json_lines = json.loads(data)
        
        panel_ids = [panel_info['Panel_Id'] for panel_info in json_lines['result']]
    
    for panel_id in panel_ids:
        panel_data = get_request(base_url.format('get_panel') + panel_id)
        
        parsed_panel = parse_panel_app_panel(
            panel_info = json.loads(panel_data)['result'], 
            hgnc_map=hgnc_map,
            institute=institute
        )
        parsed_panel['panel_id'] = panel_id
        
        if len(parsed_panel['genes']) == 0:
            LOG.warning("Panel {} is missing genes. Skipping.".format(parsed_panel['display_name']))
            continue
        
        try:
            adapter.load_panel(parsed_panel=parsed_panel)
        except Exception as err:
            raise err

        
        
    
    
    