# -*- coding: utf-8 -*-
import datetime

from flask import get_template_attribute, url_for
from pymongo import ReturnDocument

from scout.server.extensions import store


def test_report_transcripts_macro(app, institute_obj, case_obj, variant_gene_updated_info):
    """Test the variant_transcripts macro present in the general report page"""

    # Given a gene variant annotated with 3 transcripts:
    # First transcript is primary and has refseq_id
    assert variant_gene_updated_info["transcripts"][0]["refseq_id"]
    assert variant_gene_updated_info["transcripts"][0]["is_primary"] is True
    assert variant_gene_updated_info["transcripts"][0]["is_canonical"] is False

    # Second transcript has no refseq ID, is NOT primary and is NOT canonical
    assert variant_gene_updated_info["transcripts"][1].get("refseq_id") is None
    assert variant_gene_updated_info["transcripts"][1].get("is_primary") is None
    assert variant_gene_updated_info["transcripts"][1]["is_canonical"] is False

    # Third transcript is canonical
    assert variant_gene_updated_info["transcripts"][2].get("refseq_id") is None
    assert variant_gene_updated_info["transcripts"][2].get("is_primary") is None
    assert variant_gene_updated_info["transcripts"][2]["is_canonical"] is True

    # GIVEN an initialized app and a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN feeding an updated variant gene to the transcripts macro
        macro = get_template_attribute("cases/utils.html", "variant_transcripts")
        html = macro(variant_gene_updated_info)

        # THEN the transcripts visualized should be the first and the third
        assert variant_gene_updated_info["transcripts"][0]["transcript_id"] in html
        assert variant_gene_updated_info["transcripts"][2]["transcript_id"] in html

        # NOT the second
        assert variant_gene_updated_info["transcripts"][1]["transcript_id"] not in html


def test_sidebar_macro(app, institute_obj, case_obj, user_obj):
    """test the case sidebar macro"""

    # GIVEN a case with several delivery reports, both in "delivery_report" field and "analyses" field
    today = datetime.datetime.now()
    one_year_ago = today - datetime.timedelta(days=365)
    five_years_ago = today - datetime.timedelta(days=5 * 365)
    new_report = "new_delivery_report.html"
    case_analyses = [
        dict(
            # fresh analysis from today
            date=today,
            delivery_report=new_report,
        ),
        dict(
            # old analysis is 1 year old, missing the report
            date=one_year_ago,
            delivery_report=None,
        ),
        dict(
            # ancient analysis is 5 year old
            date=five_years_ago,
            delivery_report="ancient_delivery_report.html",
        ),
    ]
    # update test case with the analyses above
    case_obj["analysis_date"] = today
    case_obj["delivery_report"] = new_report
    case_obj["analyses"] = case_analyses

    # GIVEN that the case has no outdated panels
    case_obj["outdated_panels"] = []

    # update test user by adding beacon_submitter as role
    user_obj["roles"] = ["beacon_submitter"]

    # GIVEN an initialized app
    with app.test_client() as client:
        # WHEN the case sidebar macro is called
        macro = get_template_attribute("cases/collapsible_actionbar.html", "action_bar")
        html = macro(institute=institute_obj, case=case_obj, current_user=user_obj)

        # It should show the expected items:
        assert "Reports" in html
        assert "General" in html
        assert "mtDNA report" in html

        # only 2 delivery reports should be showed
        today = str(today).split(" ")[0]
        assert f"Delivery ({today})" in html

        five_years_ago = str(five_years_ago).split(" ")[0]
        assert f"Delivery ({five_years_ago})" in html

        # The analysis with missing report should not be shown
        one_year_ago = str(one_year_ago).split(" ")[0]
        assert f"Delivery ({one_year_ago})" not in html

        assert f"Genome build {case_obj['genome_build']}" in html
        assert f"Rank model" in html
        assert f"Status: {case_obj['status'].capitalize()}" in html
        assert "Assignees" in html
        assert "Research list" in html
        assert "Reruns" in html
        assert "Share case" in html


def test_sidebar_cnv_report(app, institute_obj, cancer_case_obj, user_obj):
    # GIVEN an initialized app
    with app.test_client() as client:
        # WHEN the case sidebar macro is called
        macro = get_template_attribute("cases/collapsible_actionbar.html", "action_bar")
        html = macro(institute=institute_obj, case=cancer_case_obj, current_user=user_obj)

        # It should show the expected items:
        assert "CNV report" in html
