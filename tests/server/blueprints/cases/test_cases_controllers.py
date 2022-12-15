"""Tests for the cases controllers"""
import requests
import responses
from flask import Blueprint, Flask, url_for

from scout.server.blueprints.cases.controllers import (
    case,
    coverage_report_contents,
    mt_coverage_stats,
    phenotypes_genes,
)
from scout.server.extensions import store


@responses.activate
def test_coverage_report_contents(app, institute_obj, case_obj):
    """Test the method that extracts the <body> out of HTML response from a call to chanjo-report"""

    base_url = "http://test.com/"

    # GIVEN a mocked response from chanjo-report
    responses.add(
        responses.POST,
        f"{base_url}reports/report",
        body="<html><body>This is a test</body></html>",
        status=200,
    )

    # THEN the returned result should be the HTML content included in the <body> of the HTML response
    assert coverage_report_contents(base_url, institute_obj, case_obj) == "This is a test"


def test_phenotypes_genes_research(gene_database, case_obj, hpo_term, gene_list):
    """Test function that creates phenotype terms dictionaries with gene symbol info"""
    adapter = gene_database
    # Given a database with one phenotype term containing genes
    assert adapter.hpo_term_collection.insert_one(hpo_term)

    # And a case with that dynamic phenotype and gene list
    case_obj["dynamic_panel_phenotypes"] = ["HP:0001250"]
    case_obj["dynamic_gene_list"] = [{"hgnc_id": gene_id} for gene_id in gene_list]

    # WHEN the phenotypes_genes is invoked providing test case
    pheno_dict = phenotypes_genes(adapter, case_obj, is_clinical=False)

    # THEN it should return a dictionary
    # Containing the expected term
    assert pheno_dict["HP:0001250"]["description"] == hpo_term["description"]
    # And the expected genes
    assert pheno_dict["HP:0001250"]["genes"]
    # Coresponding of all HPO term genes
    assert len(pheno_dict["HP:0001250"]["genes"].split(", ")) == len(hpo_term["genes"])


def test_phenotypes_genes_clinical(gene_database, test_case, hpo_term, panel, gene_list):
    """Test function that creates phenotype terms dictionaries with gene symbol info"""
    adapter = gene_database
    # Given a database with one phenotype term containing genes
    assert adapter.hpo_term_collection.insert_one(hpo_term)

    # given a gene panel with one of the genes from the phenotypes
    insert_panel = adapter.panel_collection.insert_one(panel)
    assert insert_panel

    # And a case with that dynamic phenotype and gene list
    test_case["dynamic_panel_phenotypes"] = ["HP:0001250"]
    test_case["dynamic_gene_list"] = [{"hgnc_id": gene_id} for gene_id in gene_list]
    # and the same panel registered for the case
    test_case["panels"][0]["panel_id"] = insert_panel.inserted_id

    ## GIVEN a variant db with the same case
    adapter.case_collection.insert_one(test_case)

    # WHEN the phenotypes_genes is invoked providing test case
    pheno_dict = phenotypes_genes(adapter, test_case, is_clinical=True)

    # THEN it should return a dictionary
    # Containing the expected term
    assert pheno_dict["HP:0001250"]["description"] == hpo_term["description"]
    # And the expected genes
    assert pheno_dict["HP:0001250"]["genes"]
    # One and only one clinical gene is now returned
    assert len(pheno_dict["HP:0001250"]["genes"].split(", ")) == 1


def test_phenotype_genes_matching_phenotypes(gene_database, case_obj, hpo_term, gene_list):
    """Test the function that creates the phenotype-genes terms dictionaries with genes matching more than 1 phenotype"""

    adapter = gene_database
    assert adapter.hgnc_collection.find_one()
    # Given a database with 2 phenotype term containing matching genes

    hpo_term2 = {
        "_id": "HP:0001298",
        "hpo_id": "HP:0001298",
        "description": "Encephalopathy",
        "genes": gene_list[:3],  # this term has last 3 genes overlapping with term 1
    }
    assert adapter.hpo_term_collection.insert_many([hpo_term, hpo_term2])
    # And a case with that dynamic phenotype and gene list
    case_obj["dynamic_panel_phenotypes"] = ["HP:0001250", "HP:0001298"]
    case_obj["dynamic_gene_list"] = [{"hgnc_id": gene_id} for gene_id in gene_list[:3]]

    # WHEN the phenotypes_genes is invoked providing test case
    pheno_dict = phenotypes_genes(adapter, case_obj, is_clinical=False)

    # THEN it should return a dictionary containing the 3 genes without associated HPO terms
    assert len(pheno_dict["Analysed genes"]["genes"].split(", ")) == 3


def test_coverage_stats(app, monkeypatch):
    """Test the function that sends requests to Chanjo to get MT vs autosomal coverage stats"""

    # GIVEN a mock connection to chanjo and an available json_chrom_coverage endpoint
    bp = Blueprint("report", __name__)

    @bp.route("/chanjo_endpoint", methods=["POST"])
    def json_chrom_coverage():
        pass

    app.register_blueprint(bp)

    def mock_post(*args, **kwargs):
        return MockResponse()

    # AND a mock response from chanjo API with coverage stats for some samples
    class MockResponse:
        def __init__(self):
            self.text = '{"sample1":36, "sample2": 32, "sample3": 34}'

    monkeypatch.setattr(requests, "post", mock_post)

    # Given a case with the same samples
    individuals = []
    samples = ["sample1", "sample2", "sample3"]
    for sample in samples:
        individuals.append({"individual_id": sample})

    with app.app_context():
        # WHEN the function to get the MT vs autosome coverage stats is invoked
        coverage_stats = mt_coverage_stats(individuals, "14")
        expected_keys = ["mt_coverage", "autosome_cov", "mt_copy_number"]
        # THEN it should return stats for each sample, and all expected key/values for each sample
        for sample in samples:
            assert sample in coverage_stats
            for key in expected_keys:
                assert key in coverage_stats[sample]


def test_case_controller_rank_model_link(adapter, institute_obj, test_case):
    # GIVEN an adapter with a case
    test_case["rank_model_version"] = "1.3"
    adapter.case_collection.insert_one(test_case)
    adapter.institute_collection.insert_one(institute_obj)
    fetched_case = adapter.case_collection.find_one()
    app = Flask(__name__)
    app.config["RANK_MODEL_LINK_PREFIX"] = "http://"
    app.config["RANK_MODEL_LINK_POSTFIX"] = ".ini"
    # WHEN fetching a case with the controller
    with app.app_context():
        data = case(adapter, institute_obj, fetched_case)
    # THEN assert that the link has been added
    assert "rank_model_link" in fetched_case


def test_case_controller(adapter, institute_obj, test_case):
    # GIVEN an adapter with a case
    adapter.case_collection.insert_one(test_case)
    adapter.institute_collection.insert_one(institute_obj)
    fetched_case = adapter.case_collection.find_one()
    app = Flask(__name__)
    # WHEN fetching a case with the controller
    with app.app_context():
        data = case(adapter, institute_obj, fetched_case)
    # THEN assert that the case have no link
    assert "rank_model_link" not in fetched_case


def test_case_controller_no_panels(adapter, institute_obj, test_case):
    # GIVEN an adapter with a case without gene panels
    adapter.case_collection.insert_one(test_case)
    adapter.institute_collection.insert_one(institute_obj)
    fetched_case = adapter.case_collection.find_one()
    assert "panel_names" not in fetched_case
    app = Flask(__name__)
    # WHEN fetching a case with the controller
    with app.app_context():
        data = case(adapter, institute_obj, fetched_case)
    # THEN
    assert fetched_case["panel_names"] == []


def test_case_controller_with_panel(app, institute_obj, panel, test_case):
    # GIVEN an adapter with a case with a gene panel
    test_case["panels"] = [
        {
            "panel_name": panel["panel_name"],
            "version": panel["version"],
            "nr_genes": 2,
            "is_default": True,
        }
    ]
    store.case_collection.insert_one(test_case)

    # GIVEN an adapter with a gene panel
    store.panel_collection.insert_one(panel)
    fetched_case = store.case_collection.find_one()
    app = Flask(__name__)
    # WHEN fetching a case with the controller
    with app.app_context():
        data = case(store, institute_obj, fetched_case)
    # THEN assert that the display information has been added to case
    assert len(fetched_case["panel_names"]) == 1


def test_case_controller_panel_wrong_version(adapter, app, institute_obj, panel, test_case):
    # GIVEN an adapter with a case with a gene panel with wrong version
    test_case["panels"] = [
        {
            "panel_name": panel["panel_name"],
            "version": panel["version"] + 1,
            "nr_genes": 2,
            "is_default": True,
        }
    ]
    adapter.case_collection.insert_one(test_case)
    adapter.institute_collection.insert_one(institute_obj)
    # GIVEN an adapter with a gene panel
    adapter.panel_collection.insert_one(panel)
    fetched_case = adapter.case_collection.find_one()

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # WHEN fetching a case with the controller
        data = case(adapter, institute_obj, fetched_case)
    # THEN assert that it succeded to fetch another panel version
    assert str(panel["version"]) in fetched_case["panel_names"][0]


def test_case_controller_non_existing_panel(adapter, app, institute_obj, test_case, panel):
    # GIVEN an adapter with a case with a gene panel but no panel objects
    test_case["panels"] = [
        {
            "panel_name": panel["panel_name"],
            "version": panel["version"] + 1,
            "nr_genes": 2,
            "is_default": True,
        }
    ]
    adapter.case_collection.insert_one(test_case)
    fetched_case = adapter.case_collection.find_one()

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # WHEN fetching a case with the controller
        data = case(adapter, institute_obj, fetched_case)
    # THEN assert that it succeded to fetch another panel version
    assert len(fetched_case["panel_names"]) == 0
