from scout.server.blueprints.variant.controllers import variant
from scout.server.extensions import (store, loqusdb)

from flask import url_for, current_app
from flask_login import current_user

def test_variant_controller(app, institute_obj, case_obj, variant_obj):
    
    ## GIVEN a populated database with a variant
    category = 'snv'
    with app.test_client() as client:
        resp = client.get(url_for('auto_login'))
        
        institute_id = institute_obj['_id']
        case_name = case_obj['display_name']
        
        var_id = variant_obj['_id']
    
        ## WHEN fetching the variant from the controller
        data = variant(store, institute_id, case_name, variant_id=var_id, add_case=True,
                add_other=True, get_overlapping=True, add_compounds=True, variant_type=category)
    
    ## THEN assert the data is on correct format
    
    assert 'overlapping_vars' in data