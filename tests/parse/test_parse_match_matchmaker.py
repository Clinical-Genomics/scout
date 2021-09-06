from scout.parse.matchmaker import parse_matches


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
