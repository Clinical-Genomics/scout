import pytest
from werkzeug.datastructures import ImmutableMultiDict

CLINICAL_TESTING = "clinical testing"

#############################################################
##################### ClinVar fixtures ######################
#############################################################


@pytest.fixture(scope="function")
def clinvar_snv_form():
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
                CLINICAL_TESTING,
                CLINICAL_TESTING,
                CLINICAL_TESTING",
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
