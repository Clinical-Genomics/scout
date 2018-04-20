from scout.server.blueprints.variants.controllers import sanger, cancel_sanger


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
