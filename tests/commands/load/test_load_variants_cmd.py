# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_load_variants(mock_app, case_obj):
    """Testing the load variants cli command"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI providing only case_id (required)
    result = runner.invoke(cli, ["load", "variants", case_obj["_id"]])
    assert result.exit_code == 0
    assert "No files where specified to upload variants from" in result.output

    # Test CLI by uploading SNV variants for a case
    result = runner.invoke(
        cli, ["load", "variants", case_obj["_id"], "--snv", "--rank-treshold", 10]
    )
    assert result.exit_code == 0

    # Test CLI by uploading SNV research variants for a case
    result = runner.invoke(cli, ["load", "variants", case_obj["_id"], "--snv-research", "--force"])
    assert result.exit_code == 0

    # Test CLI by uploading SV variants for a case
    result = runner.invoke(cli, ["load", "variants", case_obj["_id"], "--sv"])
    assert result.exit_code == 0

    # Test CLI by uploading SV research variants for a case
    result = runner.invoke(cli, ["load", "variants", case_obj["_id"], "--sv-research", "--force"])
    assert result.exit_code == 0

    # Test CLI by uploading str clinical variants for a case
    result = runner.invoke(cli, ["load", "variants", case_obj["_id"], "--str-clinical"])
    assert result.exit_code == 0

    # Test CLI by uploading variants for a hgnc_id
    result = runner.invoke(cli, ["load", "variants", case_obj["_id"], "--hgnc-id", 170])
    assert result.exit_code == 0

    # Test CLI by uploading variants for a gene symbol
    result = runner.invoke(cli, ["load", "variants", case_obj["_id"], "--hgnc-symbol", "ACTR3"])
    assert result.exit_code == 0

    # Test CLI by uploading variants for given coordinates
    result = runner.invoke(
        cli,
        [
            "load",
            "variants",
            case_obj["_id"],
            "--chrom",
            "3",
            "--start",
            60090,
            "--end",
            78000,
        ],
    )
    assert result.exit_code == 0


def test_reload_variants(mock_app, case_obj, user_obj, institute_obj):
    """Testing loading again variants after rerun"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Given an empty variant database
    assert sum(1 for i in store.variant_collection.find()) == 0

    # After using the CLI uploading SNV variants for a case
    result = runner.invoke(
        cli, ["load", "variants", case_obj["_id"], "--snv", "--rank-treshold", 10]
    )
    assert result.exit_code == 0

    # Variants collection should be populated
    assert sum(1 for i in store.variant_collection.find()) > 0

    ## Order Sanger for one variant and set it to validated
    one_variant = store.variant_collection.find_one()
    store.order_verification(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="sanger_link",
        variant=one_variant,
    )

    # then one variant should have an associated Sanger event
    assert (
        sum(1 for i in store.event_collection.find({"verb": "sanger", "category": "variant"})) == 1
    )

    store.validate(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="validated_link",
        variant=one_variant,
        validate_type="True positive",
    )

    # then one variant should have an associated Sanger event
    assert (
        sum(1 for i in store.event_collection.find({"verb": "validate", "category": "variant"}))
        == 1
    )

    # Check that the variant is validated
    new_variant = store.variant_collection.find_one({"display_name": one_variant["display_name"]})
    assert new_variant["validation"] == "True positive"

    # force re-upload the same variants using the command line:
    result = runner.invoke(
        cli,
        [
            "load",
            "variants",
            case_obj["_id"],
            "--snv",
            "--rank-treshold",
            10,
            "--force",
        ],
    )
    assert result.exit_code == 0

    # Then the variant from before should be already validated:
    new_variant = store.variant_collection.find_one({"display_name": one_variant["display_name"]})
    assert new_variant["validation"] == "True positive"

    # And 2 Sanger events shouls be found associated with the variants
    assert (
        sum(1 for i in store.event_collection.find({"verb": "sanger", "category": "variant"})) == 2
    )
