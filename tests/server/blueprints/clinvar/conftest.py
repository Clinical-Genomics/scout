import pytest
from werkzeug.datastructures import ImmutableMultiDict


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


@pytest.fixture(scope="function")
def clinvar_form(request):
    """Mocks a ClinVar form compiled by the user. Contains Variant and CaseData input data"""
    data = ImmutableMultiDict(
        {
            "case_id": "internal_id",
            "category": "snv",
            "local_id": "4c7d5c70d955875504db72ef8e1abe77",
            "linking_id": "4c7d5c70d955875504db72ef8e1abe77",
            "chromosome": "7",
            "ref": "C",
            "alt": "A",
            "start": "124491972",
            "stop": "124491972",
            "gene_symbol": "POT1",
            "last_evaluated": "2022-09-19",
            "inheritance_mode": "Autosomal dominant inheritance",
            "assertion_method": "ACMG Guidelines, 2015",
            "assertion_method_cit_db": "PMID",
            "assertion_method_cit_id": "25741868",
            "variations_ids": "rs116916706",
            "clinsig": "Likely pathogenic, low penetrance",
            "clinsig_comment": "test clinsig comment",
            "clinsig_cit": "test clinsig cit",
            "condition_comment": "test condition comment",
            "include_ind": ["NA12882"],
            "individual_id": ["NA12882", "NA12877", "NA12878"],
            "affected_status": ["yes", "no", "no"],
            "allele_of_origin": ["germline"] * 3,
            "collection_method": ["clinical testing"] * 3,
            "condition_type": "HPO",
            "conditions": ["0001298", "0001250"],
            "multiple_condition_explanation": "Novel disease",
        }
    )
    return data
