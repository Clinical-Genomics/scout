from pprint import pprint as pp

from scout.server.blueprints.dashboard.controllers import get_dashboard_info


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
