from flask import url_for

from scout.server.blueprints.variant.verification_controllers import variant_verification


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


def test_sanger_mail_str_variant(
    app,
    mock_mail,
    real_variant_database,
    institute_obj,
    case_obj,
    user_obj,
    mock_sender,
    mock_comment,
):
    """Test that an STR verification email has a short subject, and the full variant in the body"""
    adapter = real_variant_database
    ## GIVEN an STR variant with long repeat sequences in its display name
    variant_obj = adapter.variant_collection.find_one()
    long_display_name = "19_14496041_" + "TCCGCC" * 10 + "_" + "TCCGCC" * 8 + "_clinical"
    adapter.variant_collection.update_one(
        {"_id": variant_obj["_id"]},
        {
            "$set": {
                "category": "str",
                "sub_category": "str",
                "display_name": long_display_name,
                "str_repid": "GIPC1",
            }
        },
    )

    ## WHEN ordering verification for the variant
    with app.test_client() as client:
        client.get(url_for("auto_login"))

        variant_verification(
            adapter,
            institute_obj["_id"],
            case_obj["display_name"],
            variant_obj["document_id"],
            mock_sender,
            "complete_variant_url",
            "True",
            mock_comment,
            url_builder=mock_url_for,
            mail=mock_mail,
            user_obj=user_obj,
        )

    ## THEN the email subject and body use the short STR name and give the position
    message = mock_mail._message
    assert "CANCELLED" not in message.subject
    assert "STR variant GIPC1" in message.subject
    assert ">GIPC1" in message.html
    assert long_display_name not in message.subject
    ## THEN the full variant name, with the complete repeat sequences, is in the body
    assert long_display_name in message.html
    assert f"{variant_obj['chromosome']}:{variant_obj['position']}" in message.html
