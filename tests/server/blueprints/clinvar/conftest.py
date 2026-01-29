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
def clinvar_germline_snv_form():
    """Mocks a germline SNV form compiled by the user"""
    data = ImmutableMultiDict(
        {
            "affected_status": [
                "yes",
                "no",
                "no",
            ],
            "allele_of_origin": [
                "germline",
                "germline",
                "germline",
            ],
            "alt": "A",
            "assertion_method_cit_db": "PubMed",
            "assertion_method_cit_id": "12345",
            "case_id": "internal_id",
            "category": "snv",
            "chromosome": "7",
            "classification": "Pathogenic",
            "clinsig_comment": "A classification comment",
            "collection_method": [
                "clinical testing",
                "clinical testing",
                "clinical testing",
            ],
            "condition_type": "HP",
            "conditions": "0001298",
            "gene_symbol": "POT1",
            "include_ind": [
                "NA12882",
                "NA12877",
            ],
            "individual_id": [
                "NA12882",
                "NA12877",
                "NA12878",
            ],
            "inheritance_mode": "Autosomal recessive inheritance",
            "last_evaluated": "2026-01-29",
            "linking_id": [
                "4c7d5c70d955875504db72ef8e1abe77",
                "4c7d5c70d955875504db72ef8e1abe77",
                "4c7d5c70d955875504db72ef8e1abe77",
                "4c7d5c70d955875504db72ef8e1abe77",
            ],
            "local_id": "4c7d5c70d955875504db72ef8e1abe77",
            "multiple_condition_explanation": "",
            "ref": "C",
            "start": "124491972",
            "stop": "124491972",
            "submit": "Add to submission",
            "tx_hgvs": "NM_015450.3:c.903G>T",
            "variations_ids": "rs116916706",
        }
    )
    return data
