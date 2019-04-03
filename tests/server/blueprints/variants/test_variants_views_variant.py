# -*- coding: utf-8 -*-
import logging

from flask import url_for

log = logging.getLogger(__name__)

def test_server_variant(app, real_adapter):
    # GIVEN an initialized app
    # GIVEN a valid user, institute, case and variant

    adapter = real_adapter

    variant_obj = adapter.variant_collection.find_one()
    assert variant_obj

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        internal_case_id = variant_obj['case_id']
        case = adapter.case(internal_case_id)
        case_name = case['display_name']
        owner = case['owner']
        # NOTE needs the actual document_id, not the variant_id
        variant_id = variant_obj['_id']

        log.debug('Inst {} case {} variant {}'.format(owner,case_name,
                        variant_id))

        # WHEN accessing the variant page
        resp = client.get(url_for('variants.variant',
            institute_id=owner,
            case_name=case_name,
            variant_id=variant_id))

        log.debug("{}",resp.data)
        # THEN it should return a page
        assert resp.status_code == 200
