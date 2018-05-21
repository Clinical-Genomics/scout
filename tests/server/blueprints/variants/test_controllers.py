from scout.server.blueprints.variants.controllers import sanger, cancel_sanger, variants_filter_by_field



def url_for(param, institute_id, case_name, variant_id):
    pass


def test_sanger_mail_sent(mock_mail, variant_database, institute_obj, case_obj, user_obj,
                          mock_sender):
    # Given we have a variant the we want to order sanger for
    variant_obj = variant_database.variant_collection.find_one()
    variant_obj['hgnc_symbols'] = ''
    variant_obj['panels'] = ''

    # When calling sanger method
    sanger(variant_database, mock_mail, institute_obj, case_obj, user_obj, variant_obj,
           mock_sender, url_for)

    # Then the supplied mail objects send method should have been called
    assert mock_mail._send_was_called
    # Then the supplied mail objects send method should have received a message object
    assert mock_mail._message

def test_cancel_sanger_mail_sent(mock_mail, variant_database, institute_obj, case_obj, user_obj,
                          mock_sender):
    # Given we have a variant the we want to order sanger for
    variant_obj = variant_database.variant_collection.find_one()
    variant_obj['hgnc_symbols'] = ''
    variant_obj['panels'] = ''

    # When calling sanger method
    cancel_sanger(variant_database, mock_mail, institute_obj, case_obj, user_obj, variant_obj,
           mock_sender, url_for)

    # Then the supplied mail objects send method should have been called
    assert mock_mail._send_was_called
    # Then the supplied mail objects send method should have received a message object
    assert mock_mail._message


def test_collect_variants_for_case_report(case_obj, institute_obj, real_populated_database, variant_objs, parsed_variant, user_obj):
    """Test to create a dictionary similar to that used for creating a sample report"""

    adapter = real_populated_database

    # GIVEN a populated database without any variants
    assert adapter.variants(case_id=case_obj['_id'], nr_of_variants=-1).count() == 0

    # Add all variants from variant_objs
    for index, variant_obj in enumerate(variant_objs):
        adapter.load_variant(variant_obj)

    # Assert that the collections has variant documents inside
    n_documents = adapter.variant_collection.find().count()
    assert n_documents > 0

    # add useful fields to a parsed variant
    parsed_variant['display_name'] = '1_10_A_C_clinical'
    parsed_variant['case_id'] = '643594' # otherwise it won't be found later
    parsed_variant['category'] = 'snv' # used by variants_description

    # add a 'dismissed' key and value
    parsed_variant['dismiss_variant'] = ['7']
    assert 'dismiss_variant' in parsed_variant

    # upload parsed variant to database
    adapter.load_variant(parsed_variant)

    # assert that it was inserted
    assert adapter.variant_collection.find().count() == n_documents + 1

    # get all variants
    all_variants = adapter.variants(case_id=case_obj['_id'], nr_of_variants=-1)
    assert all_variants.count() > 0

    # Test that there is at least one dismissed variant to upload to the case report for this case.
    # Retrieving variants for the categories 'classified', 'commented' and 'tagged' works exactly in the same way.
    dismissed_variants = variants_filter_by_field(adapter, list(all_variants), 'dismiss_variant')
    assert len(dismissed_variants) > 0
