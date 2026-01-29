"""Fixtures for extenstions"""

import datetime

import pytest
import responses

from scout.server.app import create_app


@pytest.fixture(name="loqus_exe")
def fixture_loqus_exe():
    """Return the path to a loqus executable"""
    return "a/path/to/loqusdb"


@pytest.fixture(name="loqus_config")
def fixture_loqus_config():
    """Return the path to a loqus config"""
    return "configs/loqus-config.yaml"


@pytest.fixture
def loqus_api_variant():
    """Returns a Loqus executable instance variant"""
    variant_found = {
        "chrom": "1",
        "observations": 1,
        "families": ["643594"],
        "nr_cases": 1,
        "start": 880086,
        "end": 880087,
        "ref": "T",
        "alt": "C",
        "homozygote": 0,
        "hemizygote": 0,
        "status_code": 200,  # Added by Scout after receiving response
    }
    return variant_found


@pytest.fixture
def loqus_exe_variant():
    """Returns a Loqus executable instance variant"""
    variant_found = (
        b'{"homozygote": 0, "hemizygote": 0, "observations": 1, "chrom": "1", "start": '
        b'235918688, "end": 235918693, "ref": "CAAAAG", "alt": "C", "families": ["643594"],'
        b' "total": 3}'
    )
    return variant_found


@pytest.fixture
def loqus_exe_app(loqus_exe, loqus_config):
    """Return an app connected to LoqusDB via Loqus executable"""

    app = create_app(
        config=dict(
            TESTING=True,
            LOQUSDB_SETTINGS={
                "binary_path": loqus_exe,
                "config_path": loqus_config,
            },
        )
    )
    return app


@pytest.fixture
def loqus_api_app():
    """Return an app connected to LoqusDB via REST API"""

    app = create_app(
        config=dict(
            TESTING=True,
            LOQUSDB_SETTINGS={"api_url": "url/to/loqus/api"},
        )
    )
    return app


@pytest.fixture
def gens_app():
    """Return an app containing the Gens extension"""

    app = create_app(config=dict(TESTING=True, GENS_HOST="127.0.0.1", GENS_PORT=5000))
    return app


@pytest.fixture
def panel():
    """Return a simple panel"""
    panel_info = {
        "panel_name": "panel1",
        "display_name": "test panel",
        "institute": "cust000",
        "version": 1.0,
        "date": datetime.datetime.now(),
        "genes": [
            {"hgnc_id": 234, "symbol": "ADK"},
            {"hgnc_id": 7481, "symbol": "MT-TF"},
            {"hgnc_id": 1968, "symbol": "LYST"},
        ],
    }
    return panel_info


@pytest.fixture
def gene_list():
    """A list of HGNC ids"""
    gene_list = [26113, 9479, 10889, 18040, 10258, 1968]
    return gene_list


@pytest.fixture
def test_case(panel):
    """Return a simple case"""
    case_info = {
        "case_id": "1",
        "genome_build": 37,
        "owner": "cust000",
        "individuals": [
            {"analysis_type": "wgs", "sex": 1, "phenotype": 2, "individual_id": "ind1"}
        ],
        "status": "inactive",
        "panels": [panel],
    }
    return case_info


@pytest.fixture
def hpo_term(gene_list):
    """A test HPO term"""
    term = {
        "_id": "HP:0001250",
        "hpo_id": "HP:0001250",
        "description": "Seizure",
        "genes": gene_list,
    }
    return term


@pytest.fixture
def phenopackets_app():
    """Return an app connected to a Phenopackets API"""
    app = create_app(config=dict(TESTING=True, PHENOPAKET_API_URL="tip2toe.local"))
    return app


@pytest.fixture
def bionano_config():
    config = dict(
        TESTING=True,
        BIONANO_ACCESS="https://localhost:1234",
        BIONANO_USERNAME="USERNAME",
        BIONANO_PASSWORD="PASSWORD",
    )
    return config


@pytest.fixture
def bionano_response(bionano_config):
    TOKEN = "a_token"
    user = {
        "username": bionano_config["BIONANO_USERNAME"],
        "role": 1,
        "userpk": 1,
        "full_name": "Super User",
        "email": "clark.kent@mail.com",
    }
    bionano_response_dict = {"TOKEN": TOKEN, "user": user}
    return bionano_response_dict


@pytest.fixture
@responses.activate
def bionano_app(bionano_config, bionano_response):
    """Return an app with a bionano access extension"""

    query = f"{bionano_config['BIONANO_ACCESS']}/administration/api/1.4/login"

    responses.add(
        responses.GET,
        query,
        json={
            "output": {
                "StatusCode": 0,
                "token": bionano_response["TOKEN"],
                "user": bionano_response["user"],
            },
        },
        status=200,
        content_type="application/json",
    )

    app = create_app(config=bionano_config)
    return app


#############################################################
##################### Clinvar fixtures ######################
#############################################################
@pytest.fixture
def processed_submission() -> dict:
    """Mocks a dictionary corresponding to a processed submission coming from ClinVar.
    Copied from the ClinVar howto pages: https://www.ncbi.nlm.nih.gov/clinvar/docs/api_http/
    """

    return {
        "actions": [
            {
                "id": "SUB999999-1",
                "responses": [
                    {
                        "status": "processed",
                        "message": {
                            "errorCode": None,
                            "severity": "info",
                            "text": 'Your ClinVar submission processing status is "Success". Please find the details in the file referenced by actions[0].responses[0].files[0].url.',
                        },
                        "files": [
                            {
                                "url": "https://submit.ncbi.nlm.nih.gov/api/2.0/files/xxxxxxxx/sub999999-summary-report.json/?format=attachment"
                            }
                        ],
                        "objects": [],
                    }
                ],
                "status": "processed",
                "targetDb": "clinvar",
                "updated": "2021-03-24T04:22:04.101297Z",
            }
        ]
    }


@pytest.fixture
def successful_submission_summary_file_content() -> dict:
    """Mocks the submission summary file which is downloadable from the ClinVar API. The submission contains the status 'Success'.
    Based on the example collected from ClinVar API howto: https://www.ncbi.nlm.nih.gov/clinvar/docs/api_http/
    """

    return {
        "submissionName": "SUB673156",
        "submissionDate": "2021-03-25",
        "batchProcessingStatus": "Success",
        "batchReleaseStatus": "Not released",
        "totalCount": 1,
        "totalErrors": 0,
        "totalSuccess": 1,
        "totalPublic": 0,
        "submissions": [
            {
                "identifiers": {
                    "localID": "adefc5ed-7d59-4119-8b3d-07dcdc504c09_success1",
                    "clinvarLocalKey": "adefc5ed-7d59-4119-8b3d-07dcdc504c09_success1",
                    "localKey": "adefc5ed-7d59-4119-8b3d-07dcdc504c09_success1",
                    "clinvarAccession": "SCV000839746",
                },
                "processingStatus": "Success",
            },
        ],
    }
