# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_update_case_no_args(mock_app):
    """Tests the CLI that updates a case"""

    ## GIVEN a CLI object
    runner = mock_app.test_cli_runner()

    ## WHEN updating a case without any args
    result = runner.invoke(cli, ["update", "case"])

    ## THEN it should return an error message
    assert "Please specify which case to update" in result.output


def test_update_case_wrong_collaborator(mock_app, case_obj):
    """Tests the CLI that updates a case"""

    ## GIVEN a CLI object
    runner = mock_app.test_cli_runner()

    ## WHEN providing a case id and a collaborator whis is NOT valid
    result = runner.invoke(cli, ["update", "case", case_obj["_id"], "-c", "cust666"])

    ## THEN assert that there is a warning in the output
    assert "Institute cust666 could not be found" in result.output


def test_update_case_existing_collaborator(mock_app, case_obj):
    """Tests the CLI that updates a case"""

    ## GIVEN a CLI object
    runner = mock_app.test_cli_runner()

    ## WHEN providing a case id and a valid collaborator
    result = runner.invoke(cli, ["update", "case", case_obj["_id"], "-c", "cust000"])

    ## THEN assert that the case is fetched
    assert "INFO Fetching case {}".format(case_obj["_id"]) in result.output


def test_update_case_change_collaborator(mock_app, case_obj):
    """Tests the CLI that updates a case"""

    ## GIVEN a CLI object
    runner = mock_app.test_cli_runner()

    ## WHEN removing collaborator from case object
    store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"collaborators": []}}
    )
    res = store.case_collection.find_one({"_id": case_obj["_id"]})
    assert res["collaborators"] == []

    ## WHEN a collaborator is added via the CLI
    result = runner.invoke(cli, ["update", "case", case_obj["_id"], "-c", "cust000"])

    ## THEN assert that the operation was succesful
    assert result.exit_code == 0
    ## THEN assert that the CLI communicates relevant information
    assert "Adding collaborator" in result.output
    ## THEN assert that the collaborator was added
    res = store.case_collection.find_one({"_id": case_obj["_id"]})
    assert res["collaborators"] == ["cust000"]


def test_update_case_change_vcf_path(mock_app, case_obj, variant_clinical_file):
    """Tests the CLI that updates a case"""

    ## GIVEN a CLI object
    runner = mock_app.test_cli_runner()
    ## WHEN updating the VCF path
    result = runner.invoke(cli, ["update", "case", case_obj["_id"], "--vcf", variant_clinical_file])

    ## THEN assert it exits wothout problems
    assert result.exit_code == 0
    ## THEN assert the information is communicated
    assert "INFO Case updated" in result.output
    res = store.case_collection.find_one({"_id": case_obj["_id"]})
    ## THEN assert that the file is set correct
    assert res["vcf_files"]["vcf_snv"] == variant_clinical_file


def test_update_case_change_vcf_sv_path(mock_app, case_obj, variant_clinical_file):
    """Tests the CLI that updates a case"""

    ## GIVEN a CLI object
    runner = mock_app.test_cli_runner()

    ## WHEN updating the sv vcf path
    result = runner.invoke(
        cli, ["update", "case", case_obj["_id"], "--vcf-sv", variant_clinical_file]
    )
    ## THEN assert it exits without problems
    assert result.exit_code == 0
    ## THEN assert the information is communicated
    assert "INFO Case updated" in result.output

    res = store.case_collection.find_one({"_id": case_obj["_id"]})
    ## THEN assert that the file is set correct
    assert res["vcf_files"]["vcf_sv"] == variant_clinical_file


def test_update_case_change_vcf_cancer_path(mock_app, case_obj, variant_clinical_file):
    """Tests the CLI that updates a case"""

    ## GIVEN a CLI object
    runner = mock_app.test_cli_runner()

    ## WHEN updating the cancer vcf path
    result = runner.invoke(
        cli, ["update", "case", case_obj["_id"], "--vcf-cancer", variant_clinical_file]
    )

    ## THEN assert it exits without problems
    assert result.exit_code == 0
    ## THEN assert the information is communicated
    assert "INFO Case updated" in result.output

    res = store.case_collection.find_one({"_id": case_obj["_id"]})
    ## THEN assert that the file is set correct
    assert res["vcf_files"]["vcf_cancer"] == variant_clinical_file


def test_update_case_change_vcf_research_path(mock_app, case_obj, variant_clinical_file):
    """Tests the CLI that updates a case"""

    ## GIVEN a CLI object
    runner = mock_app.test_cli_runner()

    ## WHEN updating the research vcf path
    result = runner.invoke(
        cli,
        ["update", "case", case_obj["_id"], "--vcf-research", variant_clinical_file],
    )
    ## THEN assert it exits without problems
    assert result.exit_code == 0
    ## THEN assert the information is communicated
    assert "INFO Case updated" in result.output

    res = store.case_collection.find_one({"_id": case_obj["_id"]})
    ## THEN assert that the file is set correct
    assert res["vcf_files"]["vcf_research"] == variant_clinical_file


def test_update_case_change_sv_vcf_research_path(mock_app, case_obj, variant_clinical_file):
    """Tests the CLI that updates a case"""

    ## GIVEN a CLI object
    runner = mock_app.test_cli_runner()

    ## WHEN updating the sv research vcf path
    result = runner.invoke(
        cli,
        ["update", "case", case_obj["_id"], "--vcf-sv-research", variant_clinical_file],
    )
    ## THEN assert it exits without problems
    assert result.exit_code == 0
    ## THEN assert the information is communicated
    assert "INFO Case updated" in result.output

    res = store.case_collection.find_one({"_id": case_obj["_id"]})
    ## THEN assert that the file is set correct
    assert res["vcf_files"]["vcf_sv_research"] == variant_clinical_file


def test_update_case_change_sv_vcf_research_path(mock_app, case_obj, variant_clinical_file):
    """Tests the CLI that updates a case"""

    ## GIVEN a CLI object
    runner = mock_app.test_cli_runner()

    ## WHEN updating the sv research vcf path
    result = runner.invoke(
        cli,
        [
            "update",
            "case",
            case_obj["_id"],
            "--vcf-cancer-research",
            variant_clinical_file,
        ],
    )
    ## THEN assert it exits without problems
    assert result.exit_code == 0
    ## THEN assert the information is communicated
    assert "INFO Case updated" in result.output

    res = store.case_collection.find_one({"_id": case_obj["_id"]})
    ## THEN assert that the file is set correct
    assert res["vcf_files"]["vcf_cancer_research"] == variant_clinical_file


def test_update_case_change_sv_vcf_research_path(mock_app, case_obj, sv_clinical_file):
    """Tests the CLI that updates a case"""

    ## GIVEN a CLI object
    runner = mock_app.test_cli_runner()

    ## WHEN reuploading SVs with rank threshold

    # First save right file to upload SV variants from
    result = runner.invoke(cli, ["update", "case", case_obj["_id"], "--vcf-sv", sv_clinical_file])
    assert result.exit_code == 0
    assert "INFO Case updated" in result.output

    # then lauch the --reupload-sv command
    result = runner.invoke(
        cli,
        [
            "update",
            "case",
            case_obj["_id"],
            "--reupload-sv",
            "--rankscore-treshold",
            10,
            "--sv-rankmodel-version",
            1.5,
        ],
    )

    assert result.exit_code == 0
    assert "0 variants deleted" in result.output  # there were no variants in variant collection

    assert sum(1 for i in store.variant_collection.find({"category": "sv"})) > 0
    res = store.variant_collection.find({"category": "sv", "variant_rank": {"$gt": 10}})
    assert sum(1 for i in res) == 0
    res = store.case_collection.find({"sv_rank_model_version": 1.5})
    assert sum(1 for i in res) > 0
