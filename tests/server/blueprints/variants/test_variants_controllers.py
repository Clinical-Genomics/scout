import copy
import logging

from bson.objectid import ObjectId
from flask_wtf import FlaskForm
from pymongo import ReturnDocument
from wtforms import SelectField, StringField

from scout.constants import CANCER_EXPORT_HEADER, CHROMOSOMES_38, EXPORT_HEADER
from scout.server.blueprints.variants.controllers import (
    compounds_need_updating,
    gene_panel_choices,
    hide_compounds_query,
    match_gene_txs_variant_txs,
    populate_chrom_choices,
    sv_variants,
    update_form_hgnc_symbols,
    variant_export_lines,
    variants,
    variants_export_header,
)
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


def test_compounds_need_updating():
    """Test function that checks if variant compound objects need updating"""

    # GIVEN a list of compounds for a variant missing the "not loaded key"
    compounds = [{"variant": "aaa"}, {"variant": "bbb"}]
    # THEN the function that checks if the compounds need updating should return True
    assert compounds_need_updating(compounds, []) is True

    # GIVEN a list of dismissed variants for a case
    dismissed_variants = ["aaa", "ddd"]

    # GIVEN a list of compounds with a compound missing dismissed status
    # THEN the function that checks if the compounds need updating should return True
    assert compounds_need_updating(compounds, dismissed_variants) is True

    # GIVEN a list of compounds with a dismissed one that is not up-to-date (not in list of case dismissed variants)
    compounds = [{"variant": "ccc", "is_dismissed": True}, {"variant": "bbb"}]
    # THEN the function that checks if the compounds need updating should return True
    assert compounds_need_updating(compounds, dismissed_variants) is True

    # GIVEN an up-to-date list of compounds
    compounds = [
        {"variant": "aaa", "is_dismissed": True, "not_loaded": False},
        {"variant": "bbb", "not_loaded": True},
    ]
    # THEN the function that checks if the compounds need updating should return False
    assert compounds_need_updating(compounds, dismissed_variants) is False


def test_hide_compounds_follow_filter(app, variant_obj):
    """Test hiding compounds from view given hide compounds follow filter options"""

    # GIVEN a variant
    test_cadd = 15
    compound_variant_obj = {
        "_id": "a_compound",
        "case_id": variant_obj["case_id"],
        "chromosome": variant_obj["chromosome"],
        "position": variant_obj["position"] + 3,
        "end": variant_obj["position"] + 3,
        "reference": "A",
        "alternative": "G",
        "cadd_score": test_cadd,
        "local_obs_old": 10,
    }
    store.variant_collection.insert_one(compound_variant_obj)

    compound_variant_dict = {
        "variant": "a_compound",
        "is_dismissed": False,
    }

    # GIVEN a variant with the other variant as an only compound
    variant_obj["compounds"] = [compound_variant_dict]

    # CADD
    # WHEN asking for hiding compounds with higher cadd score threshold
    query_form = {"cadd_score": test_cadd + 1, "compound_follow_filter": True}

    # WHEN calling the function
    hide_compounds_query(store, variant_obj, query_form)

    # WHEN checking its compounds
    compounds = variant_obj.get("compounds")

    # THEN the only compound now appears dismissed
    assert compounds[0]["is_dismissed"]

    # POSITION
    # WHEN setting it back to visible
    compound_variant_dict["is_dismissed"] = False

    # WHEN asking for hiding compounds with position in the range
    query_form = {
        "position": variant_obj["position"] - 1,
        "end": variant_obj["position"] + 5,
        "compound_follow_filter": True,
    }

    # WHEN calling the function
    hide_compounds_query(store, variant_obj, query_form)

    # WHEN checking its compounds
    compounds = variant_obj.get("compounds")

    # THEN the only compound now appears dismissed
    assert compounds[0]["is_dismissed"]

    # FREQ
    # WHEN setting it back to visible
    compound_variant_dict["is_dismissed"] = False

    # WHEN asking for hiding compounds with more counts
    query_form = {"local_obs": 5, "compound_follow_filter": True}

    # WHEN calling the function
    hide_compounds_query(store, variant_obj, query_form)

    # WHEN checking its compounds
    compounds = variant_obj.get("compounds")

    # THEN the only compound now appears dismissed
    assert compounds[0]["is_dismissed"]


def test_hide_compounds_follow_filter_spidex(app, variant_obj):
    """Test hiding compounds from view given hide compounds follow filter options"""

    # GIVEN a variant
    compound_variant_obj = {
        "_id": "a_compound",
        "case_id": variant_obj["case_id"],
        "chromosome": variant_obj["chromosome"],
        "position": variant_obj["position"] + 3,
        "end": variant_obj["position"] + 3,
        "reference": "A",
        "alternative": "G",
        "spidex": -1.5,  # medium
    }
    store.variant_collection.insert_one(compound_variant_obj)

    compound_variant_dict = {
        "variant": "a_compound",
        "is_dismissed": False,
    }

    # GIVEN a variant with the other variant as an only compound
    variant_obj["compounds"] = [compound_variant_dict]

    # WHEN asking for hiding compounds with higher rank score threshold
    query_form = {"spidex_human": ["high"], "compound_follow_filter": True}

    # WHEN calling the function
    hide_compounds_query(store, variant_obj, query_form)

    # WHEN checking its compounds
    compounds = variant_obj.get("compounds")

    # THEN the only compound appears dismissed
    assert compounds[0]["is_dismissed"]

    # WHEN setting it back to visible
    compound_variant_dict["is_dismissed"] = False

    # GIVEN a variant with the other variant as an only compound
    variant_obj["compounds"] = [compound_variant_dict]

    # WHEN asking for hiding compounds within the spidex score interval
    query_form = {"spidex_human": ["medium"], "compound_follow_filter": True}

    # WHEN calling the function
    hide_compounds_query(store, variant_obj, query_form)

    # WHEN checking its compounds
    compounds = variant_obj.get("compounds")

    # THEN the only compound does not appear dismissed
    assert not compounds[0]["is_dismissed"]

    # WHEN setting it back to visible
    compound_variant_dict["is_dismissed"] = False

    # GIVEN a variant with the other variant as an only compound
    variant_obj["compounds"] = [compound_variant_dict]

    # WHEN asking for hiding compounds within a spidex score interval with both the containing and the higher level
    query_form = {"spidex_human": ["medium", "high"], "compound_follow_filter": True}

    # WHEN calling the function
    hide_compounds_query(store, variant_obj, query_form)

    # WHEN checking its compounds
    compounds = variant_obj.get("compounds")

    # THEN the only compound again appears not dismissed
    assert not compounds[0]["is_dismissed"]


def test_hide_compounds_follow_filter_region(app, variant_obj):
    """Test hiding compounds from view given hide compounds follow filter options"""

    # GIVEN a variant
    test_cadd = 15
    compound_variant_obj = {
        "_id": "a_compound",
        "case_id": variant_obj["case_id"],
        "chromosome": variant_obj["chromosome"],
        "position": variant_obj["position"] + 3,
        "end": variant_obj["position"] + 3,
        "reference": "A",
        "alternative": "G",
        "cadd_score": test_cadd,
        "spidex": -1.5,
        "local_obs_old": 10,
    }
    store.variant_collection.insert_one(compound_variant_obj)

    compound_variant_dict = {
        "variant": "a_compound",
        "is_dismissed": False,
        "region_annotations": ["exonic"],
    }

    # GIVEN a variant with the other variant as an only compound
    variant_obj["compounds"] = [compound_variant_dict]

    print("variant obj", variant_obj)
    # WHEN asking for hiding compounds that do match a region annotation
    query_form = {"region_annotations": ["exonic"], "compound_follow_filter": True}

    # WHEN calling the function
    hide_compounds_query(store, variant_obj, query_form)

    # WHEN checking its compounds
    compounds = variant_obj.get("compounds")

    # THEN the only compound now appears included
    assert compounds[0]["is_dismissed"] is False

    # but WHEN asking for hiding compounds that do not match a region annotation
    query_form = {"region_annotations": ["intronic"], "compound_follow_filter": True}

    # WHEN calling the function
    hide_compounds_query(store, variant_obj, query_form)

    # WHEN checking its compounds
    compounds = variant_obj.get("compounds")

    # THEN the only compound now appears hidden
    assert compounds[0]["is_dismissed"]

    # WHEN setting it back to visible
    compound_variant_dict["is_dismissed"] = False


def test_hide_compounds_follow_filter_in(app, variant_obj):
    """Test hiding compounds from view given hide compounds follow filter options"""

    # GIVEN a variant
    compound_variant_obj = {
        "_id": "a_compound",
        "case_id": variant_obj["case_id"],
        "chromosome": variant_obj["chromosome"],
        "position": variant_obj["position"] + 3,
        "end": variant_obj["position"] + 3,
        "reference": "A",
        "alternative": "G",
        "category": "sv",
        "sub_category": "del",
    }
    store.variant_collection.insert_one(compound_variant_obj)

    compound_variant_dict = {
        "variant": "a_compound",
        "is_dismissed": False,
    }

    # GIVEN a variant with the other variant as an only compound
    variant_obj["compounds"] = [compound_variant_dict]

    print("variant obj", variant_obj)

    # WHEN asking for hiding compounds that do match a subtype annotation
    query_form = {"svtype": ["dup", "del"], "compound_follow_filter": True}

    # WHEN calling the function
    hide_compounds_query(store, variant_obj, query_form)

    # WHEN checking its compounds
    compounds = variant_obj.get("compounds")

    # THEN the only compound now appears included
    assert compounds[0]["is_dismissed"] is False

    # WHEN asking for hiding compounds that do not match a subtype annotation
    query_form = {"svtype": ["inv"], "compound_follow_filter": True}

    # WHEN calling the function
    hide_compounds_query(store, variant_obj, query_form)

    # WHEN checking its compounds
    compounds = variant_obj.get("compounds")

    # THEN the only compound now appears dismissed
    assert compounds[0]["is_dismissed"]


def test_hide_compounds_follow_filter_clnsig(app, variant_obj):
    """Test hiding compounds from view given hide compounds follow filter options"""

    # GIVEN a variant
    compound_variant_obj = {
        "_id": "a_compound",
        "case_id": variant_obj["case_id"],
        "chromosome": variant_obj["chromosome"],
        "position": variant_obj["position"] + 3,
        "end": variant_obj["position"] + 3,
        "reference": "A",
        "alternative": "G",
        "clnsig": [{"value": "Pathogenic", "accession": "RCV00123456.7", "revstat": "single"}],
    }
    store.variant_collection.insert_one(compound_variant_obj)

    compound_variant_dict = {
        "variant": "a_compound",
        "is_dismissed": False,
    }

    # GIVEN a variant with the other variant as an only compound
    variant_obj["compounds"] = [compound_variant_dict]

    print("variant obj", variant_obj)

    # WHEN asking for hiding compounds that do match a ClinVar annotation
    query_form = {"clinsig": [4, 5], "compound_follow_filter": True}

    # WHEN calling the function
    hide_compounds_query(store, variant_obj, query_form)

    # WHEN checking its compounds
    compounds = variant_obj.get("compounds")

    # THEN the only compound appears included
    assert compounds[0]["is_dismissed"] is False


def test_hide_compounds_query_rank(app, variant_obj):
    """Test hiding compounds from view given a compound rank score filter option"""

    # GIVEN a variant
    test_rank_score = 4
    compound_variant_obj = {
        "_id": "a_compound",
        "case_id": variant_obj["case_id"],
        "chromosome": variant_obj["chromosome"],
        "position": variant_obj["position"] + 3,
        "reference": "A",
        "alternative": "G",
        "rank_score": test_rank_score,
        "is_dismissed": False,
    }
    store.variant_collection.insert_one(compound_variant_obj)

    # GIVEN a variant with the other as an only compound
    variant_obj["compounds"] = [compound_variant_obj]

    # WHEN asking for a lower score threshold
    query_form = {"compound_rank_score": test_rank_score - 1}
    # WHEN calling the function
    hide_compounds_query(store, variant_obj, query_form)

    # WHEN checking its compounds
    compounds = variant_obj.get("compounds")

    # THEN the only compound is still not dismissed
    assert compounds[0]["is_dismissed"] is False

    # WHEN asking for hiding compounds with higher rank score threshold
    query_form = {"compound_rank_score": test_rank_score + 1}
    # WHEN calling the function
    hide_compounds_query(store, variant_obj, query_form)

    # WHEN checking its compounds
    compounds = variant_obj.get("compounds")

    # THEN the only compound now appears dismissed
    assert compounds[0]["is_dismissed"]


def test_populate_chrom_choices(app):
    """Test the function that populates the choices of the chromosome select in variants filters"""

    # GIVEN a variants filter form
    with app.test_client() as client:

        class TestForm(FlaskForm):
            chrom = SelectField("Chromosome", choices=[], default="")

        form = TestForm()

    # IF the case build is 38
    case = {"genome_build": "38"}
    # THEN chromosome choices should correspond to genome build 38 chromosomes
    populate_chrom_choices(form, case)
    choices = form.chrom.choices

    for nr, choice in enumerate(choices):
        assert choice[0] == CHROMOSOMES_38[nr]


def test_gene_panel_choices(app, institute_obj, case_obj):
    """test controller function that populates gene panel filter select"""

    # GIVEN a case with a gene panel
    case_panel = {
        "panel_name": "case_panel",
        "version": 1,
        "display_name": "Case panel",
        "nr_genes": 3,
    }
    case_obj["panels"] = [case_panel]

    # AND an institute with a custom gene panel:
    institute_obj["gene_panels"] = {"institute_panel_name": "Institute Panel display name"}

    # WHEN the functions creates the option for the filters select
    panel_options = gene_panel_choices(store, institute_obj, case_obj)

    # THEN case-specific panel should be represented
    case_panel_option = (case_panel["panel_name"], case_panel["display_name"])
    assert case_panel_option in panel_options

    # HPO panel should also be represented
    assert ("hpo", "HPO") in panel_options

    # And institute-specific panel should be in the choices as well
    assert ("institute_panel_name", "Institute Panel display name") in panel_options


def test_variants_assessment_shared_with_group(
    mocker, real_variant_database, institute_obj, case_obj
):
    mocker.patch(
        "scout.server.blueprints.variants.controllers.user_institutes",
        return_value=[{"_id": "cust000"}],
    )

    # GIVEN a db with variants,
    adapter = real_variant_database
    case_id = case_obj["_id"]

    other_case_id = "other_" + case_id
    other_case_obj = copy.deepcopy(case_obj)
    other_case_obj["_id"] = other_case_id

    ## WHEN inserting an object with a group id
    group_id = ObjectId("101010101010101010101010")

    other_case_obj["group"] = [group_id]
    adapter.case_collection.insert_one(other_case_obj)

    # WHEN setting the same group id for the original case
    adapter.case_collection.find_one_and_update({"_id": case_id}, {"$set": {"group": [group_id]}})

    # GIVEN a clinical variant from one case
    variant = adapter.variant_collection.find_one({"case_id": case_id, "variant_type": "clinical"})

    # GIVEN a copy of the variant for the other case
    other_variant_obj = copy.deepcopy(variant)
    other_variant_obj["case_id"] = other_case_id
    other_variant_obj["_id"] = "another_variant"
    adapter.variant_collection.insert_one(other_variant_obj)

    # WHEN updating an assessment on the same first case variant
    adapter.variant_collection.find_one_and_update(
        {"_id": variant["_id"]}, {"$set": {"acmg_classification": 4}}
    )

    # WHEN retrieving assessments for the variant from the other case
    variants_query = {"variant_type": "clinical"}
    variants_query_res = adapter.variants(
        other_case_id, query=variants_query, category=variant["category"]
    )

    res = variants(adapter, institute_obj, other_case_obj, variants_query_res, 1000)
    res_variants = res["variants"]

    # THEN a group assessment is recalled on the other case,
    # since the variant in the first case had an annotation
    assert any(variant.get("group_assessments") for variant in res_variants)


def test_variants_research_no_shadow_clinical_assessments(
    mocker, real_variant_database, institute_obj, case_obj
):
    mocker.patch(
        "scout.server.blueprints.variants.controllers.user_institutes",
        return_value=[{"_id": "cust000"}],
    )

    # GIVEN a db with variants,
    adapter = real_variant_database
    case_id = case_obj["_id"]

    # GIVEN a clinical variant from one case
    variant_clinical = adapter.variant_collection.find_one(
        {"case_id": case_id, "variant_type": "clinical"}
    )

    # GIVEN a copy of that variant marked research
    variant_research = copy.deepcopy(variant_clinical)
    variant_research["_id"] = "research_version"
    variant_research["variant_type"] = "research"
    adapter.variant_collection.insert_one(variant_research)

    # WHEN filtering for that variant in research
    variants_query = {"variant_type": "research"}
    variants_query_res = adapter.variants(
        case_obj["_id"], query=variants_query, category=variant_clinical["category"]
    )

    # NOTE in tests list length will be used, in live code count_documents{query} is
    # called.
    number_variants = len(list(variants_query_res.clone()))

    res = variants(adapter, institute_obj, case_obj, variants_query_res, number_variants)
    res_variants = res["variants"]

    LOG.debug("Variants: {}".format(res_variants))
    # THEN it is returned
    assert any([variant["_id"] == variant_research["_id"] for variant in res_variants])

    # THEN no previous annotations are reported back for the reseach case..
    assert not any([variant.get("clinical_assessments") for variant in res_variants])


def test_variants_research_shadow_clinical_assessments(
    mocker, real_variant_database, institute_obj, case_obj
):
    mocker.patch(
        "scout.server.blueprints.variants.controllers.user_institutes",
        return_value=[{"_id": "cust000"}],
    )

    # GIVEN a db with variants,
    adapter = real_variant_database
    case_id = case_obj["_id"]

    # GIVEN a clinical variant from one case
    variant_clinical = adapter.variant_collection.find_one(
        {"case_id": case_id, "variant_type": "clinical"}
    )

    # GIVEN a copy of that variant marked research
    variant_research = copy.deepcopy(variant_clinical)
    variant_research["_id"] = "research_version"
    variant_research["variant_type"] = "research"
    adapter.variant_collection.insert_one(variant_research)

    # WHEN updating the manual assessments of the clinical variant
    adapter.variant_collection.update_one(
        {"_id": variant_clinical["_id"]},
        {
            "$set": {
                "manual_rank": 2,
                "mosaic_tags": ["1"],
                "dismiss_variant": ["2", "3"],
                "acmg_classification": 0,
            }
        },
    )

    # WHEN filtering for that variant in research
    variants_query = {"variant_type": "research"}
    variants_query_res = adapter.variants(
        case_obj["_id"], query=variants_query, category=variant_clinical["category"]
    )
    # NOTE in tests list length will be used, in live code count_documents{query} is
    # called.
    number_variants = len(list(variants_query_res.clone()))
    res = variants(adapter, institute_obj, case_obj, variants_query_res, number_variants)
    res_variants = res["variants"]

    # THEN it is returned
    assert any([variant["_id"] == variant_research["_id"] for variant in res_variants])

    # THEN previous annotations are reported back for the reseach case.
    assert any([variant.get("clinical_assessments") for variant in res_variants])


def test_sv_variants_research_shadow_clinical_assessments(
    mocker, real_variant_database, institute_obj, case_obj
):
    mocker.patch(
        "scout.server.blueprints.variants.controllers.user_institutes",
        return_value=[{"_id": "cust000"}],
    )

    # GIVEN a db with variants,
    adapter = real_variant_database
    case_id = case_obj["_id"]

    # GIVEN a clinical variant from one case
    variant_clinical = adapter.variant_collection.find_one(
        {"case_id": case_id, "variant_type": "clinical"}
    )
    # GIVEN the variant is an SV
    adapter.variant_collection.update_one(
        {"_id": variant_clinical["_id"]},
        {"$set": {"category": "sv", "sub_category": "dup"}},
    )

    # GIVEN a copy of that variant marked research
    variant_research = copy.deepcopy(variant_clinical)
    variant_research["_id"] = "research_version"
    variant_research["variant_type"] = "research"
    variant_research["category"] = "sv"
    variant_research["sub_category"]: "dup"
    adapter.variant_collection.insert_one(variant_research)

    # WHEN updating the manual assessments of the clinical variant
    adapter.variant_collection.update_one(
        {"_id": variant_clinical["_id"]},
        {
            "$set": {
                "manual_rank": 2,
                "mosaic_tags": ["1"],
                "dismiss_variant": ["2", "3"],
            }
        },
    )

    # WHEN filtering for that variant in research
    variants_query = {"variant_type": "research"}
    variants_query_res = adapter.variants(case_obj["_id"], query=variants_query, category="sv")
    assert variants_query_res
    # NOTE in tests list length will be used, in live code count_documents{query} is
    # called.
    number_variants = len(list(variants_query_res.clone()))
    res = sv_variants(adapter, institute_obj, case_obj, variants_query_res, number_variants)
    res_variants = res["variants"]

    LOG.debug("Variants: {}".format(res_variants))

    # THEN it is returned
    assert any([variant["_id"] == variant_research["_id"] for variant in res_variants])

    # THEN previous annotations are reported back for the reseach case.
    assert any([variant.get("clinical_assessments") for variant in res_variants])


def test_match_gene_txs_variant_txs():
    """Test function matching gene and variant transcripts to export variants to file"""

    variant_gene = {
        "hgnc_id": 17284,
        "transcripts": [
            {
                "transcript_id": "ENST00000357628",  # canonical
                "coding_sequence_name": "c.903G>T",
                "protein_sequence_name": "p.Gln301His",
                "is_canonical": True,
            },
            {
                "transcript_id": "ENST00000393329",  # primary
                "coding_sequence_name": "c.510G>T",
                "protein_sequence_name": "p.Gln170His",
            },
        ],
    }
    hgnc_gene = {
        "hgnc_id": 17284,
        "primary_transcripts": ["NM_001042594"],
        "transcripts": [
            {
                "ensembl_transcript_id": "ENST00000357628",  # canonical
                "refseq_identifiers": ["NM_015450"],
                "refseq_id": "NM_015450",
            },
            {
                "ensembl_transcript_id": "ENST00000393329",  # primary
                "is_primary": True,
                "refseq_identifiers": ["NM_001042594"],
                "refseq_id": "NM_001042594",
            },
        ],
    }

    canonical_txs, primary_txs = match_gene_txs_variant_txs(variant_gene, hgnc_gene)
    assert canonical_txs == ["NM_015450/c.903G>T/p.Gln301His"]
    assert primary_txs == ["NM_001042594/c.510G>T/p.Gln170His"]


def test_variant_csv_export(real_variant_database, case_obj):
    """Tests the download variants functionality for a few variants"""
    adapter = real_variant_database
    case_id = case_obj["_id"]

    # Given a database with variants from a case
    snv_variants = adapter.variant_collection.find({"case_id": case_id, "category": "snv"})

    # Given 5 variants to be exported
    variants_to_export = []
    for variant in snv_variants.limit(5):
        assert type(variant) is dict
        variants_to_export.append(variant)
    n_vars = len(variants_to_export)
    assert n_vars == 5

    # Collect export header from variants controller
    export_header = variants_export_header(case_obj)

    # Assert that exported document has n fields:
    # n = (EXPORT_HEADER items in variants_export.py) + (4 * number of individuals analysed for the case)
    assert len(export_header) == len(EXPORT_HEADER) + 4 * len(case_obj["individuals"])

    # Given the lines of the document to be exported
    export_lines = variant_export_lines(adapter, case_obj, variants_to_export)

    # Assert that all five variants are going to be exported to CSV
    assert len(export_lines) == 5

    # Assert that all of 5 variants contain the fields specified by the document header
    for export_line in export_lines:
        export_cols = export_line.split(",")
        assert len(export_cols) == len(export_header)


def test_variant_csv_export_cancer(real_variant_database, case_obj):
    """Tests the download variants functionality for a few cancer variants"""
    adapter = real_variant_database

    # GIVEN a cancer case: (let's modify a RD case to mimic a cancer case)
    case_id = case_obj["_id"]
    updated_case = adapter.case_collection.find_one_and_update(
        {"_id": case_id}, {"$set": {"track": "cancer"}}, return_document=ReturnDocument.AFTER
    )
    assert updated_case.get("track") == "cancer"

    # GIVEN a database with variants from that case
    snv_variants = adapter.variant_collection.find({"case_id": case_id, "category": "snv"})

    # Given 5 variants to be exported
    variants_to_export = []
    for variant in snv_variants.limit(5):
        variants_to_export.append(variant)

    # Collect export header from variants controller
    export_header = variants_export_header(updated_case)

    # Assert that exported document has n fields:
    # n = CANCER_EXPORT_HEADER items
    for item in export_header:
        assert item in CANCER_EXPORT_HEADER

    assert len(export_header) == len(CANCER_EXPORT_HEADER)

    # Given the lines of the document to be exported
    export_lines = variant_export_lines(adapter, updated_case, variants_to_export)

    # Assert that all five variants are going to be exported to CSV
    assert len(export_lines) == 5

    # Assert that all of 5 variants contain the fields specified by the document header
    for export_line in export_lines:
        export_cols = export_line.split(",")
        assert len(export_cols) == len(export_header)


def test_update_form_hgnc_symbols_valid_gene_symbol(app, case_obj):
    """Test controller that populates HGNC symbols form filter in variants page. Provide valid gene symbol"""

    # GIVEN a case analysed with a gene panel
    test_panel = store.panel_collection.find_one()
    case_obj["panels"] = [{"panel_id": test_panel["_id"]}]

    # GIVEN a variants filter form
    class TestForm(FlaskForm):
        hgnc_symbols = StringField()
        data = StringField()

    form = TestForm()

    # GIVEN a user trying to filter research variants using a valid gene symbol
    form.hgnc_symbols.data = ["POT1"]
    form.data = {"gene_panels": [], "variant_type": "research"}
    updated_form = update_form_hgnc_symbols(store, case_obj, form)

    # Form should be updated correctly
    assert form.hgnc_symbols.data == ["POT1"]


def test_update_form_hgnc_symbols_valid_gene_id(app, case_obj):
    """Test controller that populates HGNC symbols form filter in variants page. Provide HGNC ID"""

    # GIVEN a case analysed with a gene panel
    test_panel = store.panel_collection.find_one()
    case_obj["panels"] = [{"panel_id": test_panel["_id"]}]

    # GIVEN a variants filter form
    class TestForm(FlaskForm):
        hgnc_symbols = StringField()
        data = StringField()

    form = TestForm()

    # GIVEN a user trying to filter clinical variants using a valid gene ID
    form.hgnc_symbols.data = ["17284"]
    form.data = {"gene_panels": [], "variant_type": "clinical"}
    updated_form = update_form_hgnc_symbols(store, case_obj, form)

    # Form should be updated correctly
    assert form.hgnc_symbols.data == ["POT1"]
