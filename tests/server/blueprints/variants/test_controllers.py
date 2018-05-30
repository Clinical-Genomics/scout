from scout.server.blueprints.variants.controllers import sanger, cancel_sanger


def url_for(param, institute_id, case_name, variant_id):
    pass


def test_sanger_mail_sent(mock_mail, real_variant_database, institute_obj, case_obj, user_obj,
                          mock_sender):
    adapter = real_variant_database
    ## GIVEN we have a variant the we want to order sanger for
    variant_obj = adapter.variant_collection.find_one()
    variant_obj['hgnc_symbols'] = ''
    variant_obj['panels'] = ''

    ## WHEN calling sanger method
    sanger(adapter, mock_mail, institute_obj, case_obj, user_obj, variant_obj,
           mock_sender, url_for)

    ## THEN the supplied mail objects send method should have been called
    assert mock_mail._send_was_called
    ## THEN the supplied mail objects send method should have received a message object
    assert mock_mail._message

def test_cancel_sanger_mail_sent(mock_mail, real_variant_database, institute_obj, case_obj, user_obj,
                                  mock_sender):
    adapter = real_variant_database
    ## GIVEN we have a variant the we want to order sanger for
    variant_obj = adapter.variant_collection.find_one()
    variant_obj['hgnc_symbols'] = ''
    variant_obj['panels'] = ''

    ## WHEN calling sanger method
    cancel_sanger(adapter, mock_mail, institute_obj, case_obj, user_obj, variant_obj,
                  mock_sender, url_for)

    ## THEN the supplied mail objects send method should have been called
    assert mock_mail._send_was_called
    ## THEN the supplied mail objects send method should have received a message object
    assert mock_mail._message
