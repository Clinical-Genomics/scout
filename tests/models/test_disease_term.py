import pytest

from scout.models.disease_term import DiseaseTerm


@pytest.mark.parametrize("key", ["description", "source", "disease_nr", "disease_id"])
def test_diseaseterm(key):
    """Tests validation of disease_terms asserting it fails if required information is missing"""
    # GIVEN a dictionary representing a disease_object

    test_disease_obj = {
        "disease_nr": 431341,
        "disease_id": "ORPHA:431341",
        "source": "ORPHA",
        "hpo_terms": [
            "HP:0034267",
            "HP:0000010",
            "HP:0010957",
            "HP:0032435",
            "HP:0010881",
            "HP:0002027",
            "HP:0010479",
            "HP:0012618",
            "HP:0005420",
            "HP:0100645",
        ],
        "inheritance": [],
        "description": "Patent urachus",
        "genes": [],
        "_id": "ORPHA:431341",
    }
    # WHEN deleting a mandatory key
    test_disease_obj.pop(key)
    # THEN calling DiseaseTerm will raise ValueError
    with pytest.raises(ValueError):
        DiseaseTerm(**test_disease_obj)
