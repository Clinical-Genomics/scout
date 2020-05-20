from scout.server.blueprints.variant.verification_controllers import variant_verification
from flask import url_for


def mock_url_for(param, institute_id, case_name, variant_id):
    pass


def test_sanger_mail_sent(
    app,
    mock_mail,
    real_variant_database,
    institute_obj,
    case_obj,
    user_obj,
    mock_sender,
    mock_comment,
):
    adapter = real_variant_database
    ## GIVEN we have a variant the we want to order sanger for
    institute_id = institute_obj["_id"]
    case_name = case_obj["display_name"]
    variant_obj = adapter.variant_collection.find_one()
    variant_obj["hgnc_symbols"] = ""
    variant_obj["panels"] = ""
    variant_id = variant_obj["document_id"]

    ## WHEN calling variant_verification method with order==True
    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))

        variant_verification(
            adapter,
            institute_id,
            case_name,
            variant_id,
            mock_sender,
            "complete_variant_url",
            True,
            mock_comment,
            url_builder=mock_url_for,
            mail=mock_mail,
            user_obj=user_obj,
        )

    ## THEN the supplied mail objects send method should have been called
    assert mock_mail._send_was_called
    ## THEN the supplied mail objects send method should have received a message object
    assert mock_mail._message


def test_cancel_sanger_mail_sent(
    app,
    mock_mail,
    real_variant_database,
    institute_obj,
    case_obj,
    user_obj,
    mock_sender,
    mock_comment,
):
    adapter = real_variant_database
    ## GIVEN we have a variant the we want to order sanger for
    institute_id = institute_obj["_id"]
    case_name = case_obj["display_name"]
    variant_obj = adapter.variant_collection.find_one()
    variant_obj["hgnc_symbols"] = ""
    variant_obj["panels"] = ""
    variant_id = variant_obj["document_id"]

    ## WHEN calling variant_verification method with order==False
    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))

        variant_verification(
            adapter,
            institute_id,
            case_name,
            variant_id,
            mock_sender,
            "complete_variant_url",
            False,
            mock_comment,
            url_builder=mock_url_for,
            mail=mock_mail,
            user_obj=user_obj,
        )

    ## THEN the supplied mail objects send method should have been called
    assert mock_mail._send_was_called
    ## THEN the supplied mail objects send method should have received a message object
    assert mock_mail._message
