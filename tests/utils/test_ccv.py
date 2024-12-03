from scout.utils.ccv import get_ccv, get_ccv_conflicts, get_ccv_temperature


def test_get_ccv_no_terms():
    ccv_terms = set()
    res = get_ccv(ccv_terms)
    assert res is None


def test_get_ccv_oncogenic():
    ccv_terms = {"OVS1", "OS1"}
    res = get_ccv(ccv_terms)
    assert res == "oncogenic"

    ccv_terms = {"OP1", "OP4", "OM2", "OM3", "OS1"}
    res = get_ccv(ccv_terms)
    assert res == "oncogenic"


def test_get_ccv_likely_oncogenic():
    ccv_terms = {"OVS1"}
    res = get_ccv(ccv_terms)
    assert res == "likely_oncogenic"

    ccv_terms = {"OP1", "OP4", "OM2", "OM3"}
    res = get_ccv(ccv_terms)
    assert res == "likely_oncogenic"


def test_get_ccv_benign():
    ccv_terms = {"OP1", "SBVS1"}
    res = get_ccv(ccv_terms)
    assert res == "benign"

    ccv_terms = {"SBP1", "SBP2", "SBS1", "SBS2"}
    res = get_ccv(ccv_terms)
    assert res == "benign"


def test_get_ccv_likely_benign():
    ccv_terms = {"OP1", "SBS2"}
    res = get_ccv(ccv_terms)
    assert res == "likely_benign"

    ccv_terms = {"SBP1", "SBP2"}
    res = get_ccv(ccv_terms)
    assert res == "likely_benign"


def test_get_ccv_uncertain():
    ccv_terms = {"OM3"}
    res = get_ccv(ccv_terms)
    assert res == "uncertain_significance"

    ccv_terms = {"OP1", "OP2", "OP3", "OP4", "SBP1"}
    res = get_ccv(ccv_terms)
    assert res == "uncertain_significance"


def test_get_ccv_oncogenic_modifier():
    ccv_terms = {"OVS1", "OS1"}
    res = get_ccv(ccv_terms)
    assert res == "oncogenic"

    ccv_terms = {"OVS1_Moderate", "OS1"}
    res = get_ccv(ccv_terms)
    assert res == "likely_oncogenic"


def test_ccv_modifier_on_both_benign_and_oncogenic():
    ccv_terms = {"OS3_Moderate", "OS1_Moderate", "OP3", "SBP1_Strong"}
    res = get_ccv(ccv_terms)
    assert res == "uncertain_significance"


def test_ccv_benign_modifier():
    ccv_terms = {"SBP1_Moderate", "SBP2_Moderate", "SBS1"}
    res = get_ccv(ccv_terms)
    assert res == "benign"

    ccv_terms = {"SBVS1_Supporting", "SBS1_Supporting"}
    res = get_ccv(ccv_terms)
    assert res == "likely_benign"


def test_ccv_conflicts():
    ccv_terms = {"OS2", "OS1"}
    conflicts = get_ccv_conflicts(ccv_terms)
    assert len(conflicts) == 1


def test_ccv_temperature():
    ccv_terms = {"OVS1", "OS1", "OM1", "SBVS1", "SBP2"}
    res = get_ccv_temperature(ccv_terms)
    assert res["points"] == 5
    assert res["temperature"] == "Hot"
    assert res["point_classification"] == "VUS"

    ccv_terms = {"OM3", "OM2", "OP3", "SBP1"}
    res = get_ccv_temperature(ccv_terms)
    assert res["points"] == 4
    assert res["temperature"] == "Warm"
    assert res["point_classification"] == "VUS"

    ccv_terms = {"OS2", "OS3", "OM4", "OP4", "SBS1", "SBS2"}
    res = get_ccv_temperature(ccv_terms)
    assert res["points"] == 3
    assert res["temperature"] == "Tepid"
    assert res["point_classification"] == "VUS"
