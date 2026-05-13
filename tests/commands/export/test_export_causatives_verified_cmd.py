# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.constants.managed_variant import MANAGED_VARIANTS_INFILE_HEADER
from scout.server.extensions import store


def test_export_causatives(mock_app, institute_obj, case_obj, user_obj):
    """Test the CLI command that exports causatives into vcf format"""

    runner = mock_app.test_cli_runner()
    assert runner

    # There are no variants in mock app database
    assert store.variant_collection.find_one() is None

    # Load snv variants using the cli
    runner.invoke(cli, ["load", "variants", case_obj["_id"], "--snv"])
    assert sum(1 for _ in store.variant_collection.find()) > 0

    ## WHEN marking a variant as causative
    variant_obj = store.variant_collection.find_one()
    link = "markCausativelink"
    store.mark_causative(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=variant_obj,
    )
    assert store.event_collection.find(
        {
            "institute": "cust000",
            "verb": {"$in": ["mark_causative", "mark_partial_causative"]},
            "category": "case",
        }
    )

    # Test the CLI by not providing any options or arguments
    result = runner.invoke(cli, ["export", "causatives"])
    assert result.exit_code == 0
    assert "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO" in result.output
    # variant should be returned
    assert str(variant_obj["position"]) in result.output

    # Test the CLI by providing wrong collaborator
    result = runner.invoke(cli, ["export", "causatives", "-c", "cust666"])
    assert result.exit_code == 0
    assert "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO" in result.output
    # variant should NOT be returned
    assert str(variant_obj["position"]) not in result.output

    # Test the CLI by providing the right collaborator, build and variant type
    result = runner.invoke(
        cli, ["export", "causatives", "-c", case_obj["owner"], "--build", "37", "--category", "snv"]
    )
    assert result.exit_code == 0
    assert "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO" in result.output
    # variant should be returned
    assert str(variant_obj["position"]) in result.output

    # Test the CLI by providing the document_id of the variant
    result = runner.invoke(cli, ["export", "causatives", "-d", variant_obj["document_id"]])
    assert result.exit_code == 0
    assert "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO" in result.output
    # variant should be returned
    assert str(variant_obj["position"]) in result.output

    # Test the CLI by providing the case_id of the variant
    result = runner.invoke(cli, ["export", "causatives", "--case-id", case_obj["_id"]])
    assert result.exit_code == 0
    assert "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO" in result.output
    # variant should be returned
    assert str(variant_obj["position"]) in result.output

    # Test the CLI by providing the case_id of the variant and and json option
    result = runner.invoke(cli, ["export", "causatives", "--case-id", case_obj["_id"], "--json"])
    assert result.exit_code == 0
    assert "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO" not in result.output
    # variant should be returned
    assert str(variant_obj["position"]) in result.output
    assert '"position": {}'.format(variant_obj["position"]) in result.output

    # Test the CLI option to export causatives to a managed variants infile
    result = runner.invoke(
        cli, ["export", "causatives", "--as-managed", "--managed-link-base-url", "fakeurl"]
    )
    assert result.exit_code == 0
    # variant should be returned
    assert MANAGED_VARIANTS_INFILE_HEADER in result.output
    assert str(variant_obj["position"]) in result.output


def test_export_verified(mock_app, case_obj, user_obj, institute_obj):
    """Test the CLI command that exports verified variants into excel files"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Load snv variants using the cli
    runner.invoke(cli, ["load", "variants", case_obj["_id"], "--snv"])

    assert store.variant_collection.find_one() is not None

    # Test the cli without verified variants available
    result = runner.invoke(cli, ["export", "verified"])
    assert result.exit_code == 0
    assert "There are no verified variants for institute cust000 in database!" in result.output

    # Set a variant as verified
    variant_obj = store.variant_collection.find_one()

    # Validate the above variant:
    store.validate(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="link_to_var",
        variant=variant_obj,
        validate_type="True positive",
    )
    var_res = store.variant_collection.find({"validation": "True positive"})
    assert sum(1 for _ in var_res) == 1
    event_res = store.event_collection.find({"verb": "validate"})
    assert sum(1 for _ in event_res) == 1

    # Test the cli without parameters
    result = runner.invoke(cli, ["export", "verified", "--test"])
    assert result.exit_code == 0
    # Variant should be found now
    assert "Success. Verified variants file contains" in result.output

    # Test the cli with with a wrong collaborator param
    result = runner.invoke(cli, ["export", "verified", "--test", "-c", "cust666"])
    assert result.exit_code == 0
    # Variant should not be found now
    assert "There are no verified variants for institute cust666 in database!" in result.output

    # Test the cli with the right collaborator param
    result = runner.invoke(cli, ["export", "verified", "--test", "-c", case_obj["owner"]])
    assert result.exit_code == 0
    # Variant should be found again
    assert "Success. Verified variants file contains" in result.output


def test_export_managed(mock_app):
    """Test the CLI command for exporting managed variants"""

    # GIVEN a mock app runner
    runner = mock_app.test_cli_runner()
    assert runner

    # WHEN invoking the CLI command
    result = runner.invoke(cli, ["export", "managed", "--build", "37"])
    assert result.exit_code == 0

    # THEN a VCF is output
    assert "#CHROM" in result.output
