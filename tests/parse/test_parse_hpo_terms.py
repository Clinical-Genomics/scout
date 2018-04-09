from scout.parse.hpo import (parse_hpo_phenotype, parse_hpo_phenotypes, parse_hpo_obo)

def test_parse_hpo_line():
    ## GIVEN a line that describes a hpo term
    hpo_line = "HP:0000878\t11 pairs of ribs\t126792\tB3GALT6"
    ## WHEN parsing the line
    hpo_info = parse_hpo_phenotype(hpo_line)
    ## THEN assert that the correct information was parsed
    assert hpo_info['hpo_id'] == "HP:0000878"
    assert hpo_info['description'] == "11 pairs of ribs"
    assert hpo_info['hgnc_symbol'] == "B3GALT6"

def test_parse_hpo_lines():
    ## GIVEN some lines that correspends to a hpo file
    hpo_lines = [
        "#Format: HPO-ID<tab>HPO-Name<tab>Gene-ID<tab>Gene-Name",
        "HP:0000878\t11 pairs of ribs\t126792\tB3GALT6",
        "HP:0000878\t11 pairs of ribs\t5932\tRBBP8"
    ]
    ## WHEN parsing the lines
    hpo_dict = parse_hpo_phenotypes(hpo_lines)
    ## THEN assert that the correct information was parsed
    assert len(hpo_dict) == 1
    assert "HP:0000878" in hpo_dict
    assert set(hpo_dict['HP:0000878']['hgnc_symbols']) == set(['B3GALT6', 'RBBP8'])

def test_parse_hpo_obo():
    hpo_info = [
        "[Term]",
        "id: HP:0000003",
        "name: Multicystic kidney dysplasia",
        "alt_id: HP:0004715",
        "def: Multicystic dysplasia of the kidney is characterized by multiple cysts of varying size in the kidney and the absence of a normal pelvicaliceal system. The condition is associated with ureteral or ureteropelvic atresia, and the affected kidney is nonfunctional. [HPO:curators]",
        "comment: Multicystic kidney dysplasia is the result of abnormal fetal renal development in which the affected kidney is replaced by multiple cysts and has little or no residual function. The vast majority of multicystic kidneys are unilateral. Multicystic kidney can be diagnosed on prenatal ultrasound.",
        'synonym: "Multicystic dysplastic kidney" EXACT []',
        'synonym: "Multicystic kidneys" EXACT []',
        'synonym: "Multicystic renal dysplasia" EXACT []',
        "xref: MSH:D021782",
        "xref: SNOMEDCT_US:204962002",
        "xref: SNOMEDCT_US:82525005",
        "xref: UMLS:C3714581",
        "is_a: HP:0000107 ! Renal cyst",
        
    ]
    hpo_terms = parse_hpo_obo(hpo_info)
    
    for hpo_term in hpo_terms:
        assert hpo_term['hpo_id'] == "HP:0000003"
        assert hpo_term['description'] == "Multicystic kidney dysplasia"

def test_parse_hpo_terms(hpo_terms_handle):
    hpo_terms = parse_hpo_obo(hpo_terms_handle)
    
    for hpo_term in hpo_terms:
        assert hpo_term['hpo_id']
