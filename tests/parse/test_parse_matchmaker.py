import pytest

from scout.parse.matchmaker import genomic_features, hpo_terms, omim_terms, parse_matches


def test_parse_hpo_terms(case_obj, test_hpo_terms):
    """Test extracting and formatting HPO terms from a case for a MatchMaker submission"""

    # GIVEN a case with HPO terms
    case_obj["phenotype_terms"] = test_hpo_terms

    # THEN the hpo_terms function shuld extract them and organize them as MatchMaker features
    features = hpo_terms(case_obj)
    assert len(features) == len(test_hpo_terms)
    for feature in features:
        assert feature["id"]
        assert feature["label"]
        assert feature["observed"] == "yes"


@pytest.mark.parametrize("key", [("disease_nr"), ("disease_id")])
def test_omim_terms(adapter, case_obj, test_omim_database_term, key):
    """Test extracting and formatting OMIM terms from a case for a MatchMaker submission"""

    # GIVEN a database containing an OMIM term
    adapter.disease_term_collection.insert_one(test_omim_database_term)

    # GIVEN a case with OMIM terms
    case_obj["diagnosis_phenotypes"] = [test_omim_database_term[key]]

    # THEN the omim_terms function should extract OMIM terms with an ID and a label
    disorders = omim_terms(adapter, case_obj)
    assert disorders[0]["id"] == f"MIM:{test_omim_database_term['disease_nr']}"
    assert disorders[0]["label"] == test_omim_database_term["description"]


def test_genomic_features(real_variant_database, case_obj):
    """Test function that parses pinned variants from a case and returns them as MatchMaker genomic features"""

    # GIVEN a case with a pinned variant that is in the database
    adapter = real_variant_database
    test_variant = adapter.variant_collection.find_one({"hgnc_symbols": ["POT1"]})

    case_obj["suspects"] = [test_variant["_id"]]
    sample_name = "NA12882"

    # WHEN the parse genomic_features is used to parse genotype features of this case
    g_features = genomic_features(
        store=adapter,
        case_obj=case_obj,
        sample_name=sample_name,
        candidate_vars=case_obj["suspects"],
        genes_only=False,
    )
    # THEN it should return the expected data
    assert isinstance(g_features, list)
    assert g_features[0]["gene"] == {"id": "POT1"}
    assert isinstance(g_features[0]["variant"], dict)


def test_parse_matches(case_obj, match_objs):
    """tests that a list of MatchMaker matches returned by the server is interpreted
    as it should
    """
    case_id = case_obj["_id"]
    affected_id = ""

    for individual in case_obj["individuals"]:
        if individual["phenotype"] == "affected":
            affected_id = individual["individual_id"]
            assert affected_id

    # scout patient's id in matchmaker database is composed like this
    # scout_case_id.affected_individual_id
    mme_patient_id = ".".join([case_id, affected_id])

    # make sure that results are returned by parsing matching object
    parsed_obj = parse_matches(mme_patient_id, match_objs)

    assert isinstance(parsed_obj, list)
    # mme_patient_id has matches in match_objs:
    assert len(parsed_obj) == 2

    for match in parsed_obj:
        # make sure that all important fields are available in match results
        assert match["match_oid"]
        assert match["match_date"]
        matching_patients = match["patients"]
        for m_patient in matching_patients:
            assert m_patient["patient_id"]
            assert m_patient["node"]
            assert m_patient["score"]
            assert m_patient["patient"]
