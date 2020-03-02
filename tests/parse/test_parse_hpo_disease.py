from scout.parse.hpo import parse_hpo_disease, parse_hpo_diseases


def test_parse_disease_lines():
    """Test how the parser behaves"""
    disease_lines = [
        "#Format: HPO-id<tab>HPO label<tab>entrez-gene-id<tab>entrez-gene-symbol<tab>Additional Info from G-D source<tab>G-D source<tab>disease-ID for link",
        "HP:0000002	Abnormality of body height	3954	LETM1	-	mim2gene	OMIM:194190",
    ]
    ## GIVEN a disease term without gene symbol
    ## WHEN parsing the line
    disease = parse_hpo_disease(disease_lines[1])
    ## THEN assert the info is correct
    assert disease["source"] == "OMIM"
    assert disease["disease_nr"] == 194190
    assert disease["hgnc_symbol"] == "LETM1"


def test_parse_diseases_lines():
    ## GIVEN a iterable of disease lines
    disease_lines = [
        "#Format: HPO-id<tab>HPO label<tab>entrez-gene-id<tab>entrez-gene-symbol<tab>Additional Info from G-D source<tab>G-D source<tab>disease-ID for link",
        "HP:0004426	Abnormality of the cheek	54880	BCOR		orphadata	ORPHA:568",
        "HP:0004429	Recurrent viral infections	919	CD247		orphadata	ORPHA:169160",
        "HP:0004431	Complement deficiency	713	C1QB	-	mim2gene	OMIM:613652",
        "HP:0004426	Abnormality of the cheek	2263	FGFR2		orphadata	ORPHA:1555"
    ]
    ## WHEN parsing the diseases
    diseases = parse_hpo_diseases(disease_lines)
    ## THEN assert that the diseases are parsed correct
    assert diseases["OMIM:613652"]["source"] == "OMIM"
    assert diseases["OMIM:613652"]["hgnc_symbols"] == set(["C1QB"])


def test_parse_diseases(hpo_disease_handle):
    ## GIVEN a iterable of disease lines
    ## WHEN parsing the diseases
    diseases = parse_hpo_diseases(hpo_disease_handle)
    ## THEN assert that the diseases are parsed correct
    for disease_id in diseases:
        source = disease_id.split(":")[0]
        disease_nr = int(disease_id.split(":")[1])

        disease_term = diseases[disease_id]
        assert disease_term["source"] == source
        assert disease_term["disease_nr"] == disease_nr
