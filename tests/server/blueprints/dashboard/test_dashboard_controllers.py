from flask import url_for

from scout.server.blueprints.dashboard.controllers import (
    compose_slice_query,
    dashboard_form,
    get_dashboard_info,
    institute_select_choices,
)
from scout.server.blueprints.dashboard.forms import DashboardFilterForm
from scout.server.extensions import store


def test_institute_select_choices(user_obj, app):
    """Test the function that creates the data for the institute select"""

    # GIVEN an app with a logged user
    with app.test_client() as client:

        resp = client.get(url_for("auto_login"))

        # WHEN returning the institute institute select choices
        select_choices = institute_select_choices()

        # It should return the expected list of tuples
        assert len(select_choices) == len(user_obj["institutes"]) + 1
        assert select_choices[0] == ("All", "All institutes")
        user_institute = user_obj["institutes"][0]
        assert select_choices[1][0] == user_institute


def test_dashboard_form(app):
    """Test the function returning the dashboard page form"""

    # GIVEN an app with a logged user
    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))

        # A DashboardFilterForm should be created correctly by dashboard_form
        df = dashboard_form(None)
        assert isinstance(df, DashboardFilterForm)
        assert df.search_type
        assert df.search_institute
        assert df.search_term
        assert df.search


def test_compose_slice_query(app):
    """Test function that combines form fields to create filter query"""

    # GIVEN two parameters provided in the dashboard filter form
    search_type = "case:"
    search_term = "test_case"
    slice_query = compose_slice_query(search_type, search_term)
    assert slice_query == f"{search_type}{search_term}"


def test_empty_database(real_adapter):
    ## GIVEN an empty database
    adapter = real_adapter
    ## WHEN asking for data
    data = get_dashboard_info(adapter)
    ## THEN assert that the data is empty
    assert data.get("total_cases") == 0


def test_one_case(real_adapter, case_obj):
    ## GIVEN an database with one case
    adapter = real_adapter
    adapter._add_case(case_obj)

    ## WHEN asking for data
    data = get_dashboard_info(adapter)
    ## THEN assert there is one case in the data
    for group in data["cases"]:
        if group["status"] == "all":
            assert group["count"] == 1
        elif group["status"] == case_obj["status"]:
            assert group["count"] == 1


def test_one_causative(real_adapter, case_obj):
    ## GIVEN an database with two cases where one has a causative
    adapter = real_adapter
    adapter._add_case(case_obj)
    case_obj["causatives"] = ["a variant"]
    case_obj["_id"] = "test1"
    adapter._add_case(case_obj)
    ## WHEN asking for data
    institute_id = case_obj["owner"]
    data = get_dashboard_info(adapter, institute_id=institute_id)
    ## THEN assert there is one case in the causative information
    for info in data["overview"]:
        if info["title"] == "Causative variants":
            assert info["count"] == 1
        else:
            assert info["count"] == 0


def test_with_slice_query(real_adapter, case_obj):
    ## GIVEN an database with one case
    adapter = real_adapter
    adapter._add_case(case_obj)
    ## WHEN asking for data
    case_display_id = case_obj["display_name"]

    institute_id = case_obj["owner"]

    slice_query = f"case:{case_display_id}"
    data = get_dashboard_info(adapter, institute_id=institute_id, slice_query=slice_query)

    ## THEN assert there is one case in the data
    for group in data["cases"]:
        if group["status"] == "all":
            assert group["count"] == 1
        elif group["status"] == case_obj["status"]:
            assert group["count"] == 1


def test_with_hpo_query(real_adapter, case_obj):
    ## GIVEN an database with one case
    adapter = real_adapter
    adapter._add_case(case_obj)
    phenotype = {"phenotype_id": "HP:0000001", "feature": "Bioterm"}

    ## WITH a phenotype set for one case
    case_obj["phenotype_terms"] = [phenotype]
    case_obj["_id"] = "test1"
    adapter._add_case(case_obj)

    ## WHEN querying for cases with that phenotype id
    institute_id = case_obj["owner"]
    slice_query = f"exact_pheno:{phenotype['phenotype_id']}"

    data = get_dashboard_info(adapter, institute_id=institute_id, slice_query=slice_query)
    ## THEN assert there is one case in the data
    for group in data["cases"]:
        if group["status"] == "all":
            assert group["count"] == 1
        elif group["status"] == case_obj["status"]:
            assert group["count"] == 1


def test_with_phenotype_group_query(real_adapter, case_obj):
    ## GIVEN an database with one case
    adapter = real_adapter
    adapter._add_case(case_obj)
    phenotype = {"phenotype_id": "HP:0000001", "feature": "Bioterm"}

    ## WITH a phenotype set for one case
    case_obj["phenotype_groups"] = [phenotype]
    case_obj["_id"] = "test1"
    adapter._add_case(case_obj)

    ## WHEN querying for cases with that phenotype id
    institute_id = case_obj["owner"]
    slice_query = "pheno_group:HP:0000001"

    data = get_dashboard_info(adapter, institute_id=institute_id, slice_query=slice_query)
    ## THEN assert there is one case in the data
    for group in data["cases"]:
        if group["status"] == "all":
            assert group["count"] == 1
        elif group["status"] == case_obj["status"]:
            assert group["count"] == 1
