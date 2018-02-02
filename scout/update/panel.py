import logging

LOG = logging.getLogger(__name__)

def update_panel(adapter, panel_name, panel_version, new_version=None, new_date=None):
    """docstring for update_panel"""
    panel_obj = adapter.gene_panel(panel_name, panel_version)
    
    updated_panel = adapter.update_panel(panel_obj, new_version, new_date)
    
    panel_id = updated_panel['_id']
    
    
    # We need to alter the embedded panels in all affected cases
    update = {'$set': {}}
    if new_version:
        update['$set']['panels.$.version'] = updated_panel['version']
    if new_date:
        update['$set']['panels.$.updated_at'] = updated_panel['date']
    
    LOG.info('Updating affected cases with {0}'.format(update))
    
    query = {'panels': { '$elemMatch': {'panel_id': panel_id}}}
    adapter.case_collection.update_many(query, update)
    
    return updated_panel