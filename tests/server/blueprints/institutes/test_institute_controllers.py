import copy

from werkzeug.datastructures import MultiDict

from scout.server.blueprints.institutes.controllers import cases, phenomodel_checkgroups_filter
from scout.server.extensions import store


def test_phenomodel_checkgroups_filter(app, institute_obj, hpo_checkboxes, omim_checkbox):
    """Test the controllers function that updates the phenotype model based on the model preview checkbox preferences"""
    # GIVEN a database with the required HPO terms (one parent term and one child term)
    store.hpo_term_collection.insert_many(hpo_checkboxes)

    # GIVEN a phenotype model with one panel and 3 checkboxes (checkbox2 nested inside checkbox1)
    hpo_id1 = hpo_checkboxes[0]["_id"]
    hpo_id2 = hpo_checkboxes[1]["_id"]
    omim_id = omim_checkbox["_id"]
    checkbox2 = dict(
        name=hpo_id2,
        description=hpo_checkboxes[1]["description"],
    )
    checkbox1 = dict(
        name=hpo_id1,
        description=hpo_checkboxes[1]["description"],
        children=[checkbox2],  # nested checkbox with HPO term 2
    )
    checkbox3 = {"name": omim_id, "description": omim_checkbox["description"]}
    test_model = dict(
        institute=institute_obj["_id"],
        name="Test model",
        subpanels=dict(panel1=dict(checkboxes={hpo_id1: checkbox1, omim_id: checkbox3})),
    )
    store.phenomodel_collection.insert_one(test_model)
    model_obj = store.phenomodel_collection.find_one()
    # THEN 2 checkboxes should show at the top level
    assert model_obj["subpanels"]["panel1"]["checkboxes"][hpo_id1]
    assert model_obj["subpanels"]["panel1"]["checkboxes"][omim_id]
    assert hpo_id2 not in model_obj["subpanels"]["panel1"]["checkboxes"]

    with app.app_context():
        # WHEN phenotype checkboxes are updated to keep only the nested checkbox2
        checked_terms = MultiDict({"cheked_terms": [".".join(["panel1", hpo_id1, hpo_id2])]})
        updated_model = phenomodel_checkgroups_filter(model_obj, checked_terms)
        # THEN the right checkbox should be present in submodel checkboxes dictionary
        assert updated_model["subpanels"]["panel1"]["checkboxes"][hpo_id2]
        assert hpo_id1 not in updated_model["subpanels"]["panel1"]["checkboxes"]
        assert omim_id not in updated_model["subpanels"]["panel1"]["checkboxes"]
