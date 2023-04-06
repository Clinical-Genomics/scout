import pytest


@pytest.fixture
def omim_checkbox():
    """Returns a dictionaries representing an OMIM checkboxe"""
    checkbox = {
        "disease_id": "OMIM:121210",
        "description": "Febrile seizures familial 1",
    }
    return checkbox


@pytest.fixture
def hpo_checkboxes():
    """Returns a list of dictionaries representing HPO checkboxes"""
    checkbox1 = {
        "_id": "HP:0025190",
        "hpo_id": "HP:0025190",
        "description": "Bilateral tonic-clonic seizure with generalized onset",
        "children": ["HP:0032661"],
        "ancestors": [],
    }
    checkbox2 = {
        "_id": "HP:0032661",
        "hpo_id": "HP:0032661",
        "description": "Generalized convulsive status epilepticus",
        "children": [],
        "ancestors": ["HP:0025190"],
    }
    return [checkbox1, checkbox2]
