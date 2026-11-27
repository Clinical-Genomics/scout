from scout.parse.clingen import get_clingen_disease_terms, parse_clingen_gene_validity_csv

HEADER = [
    '"CLINGEN GENE DISEASE VALIDITY CURATIONS","","","","","","","","",""',
    '"FILE CREATED: 2026-11-25","","","","","","","","",""',
    '"WEBPAGE: https://search.clinicalgenome.org/kb/gene-validity","","","","","","","","",""',
    '"+++++++++++","++++++++++++++","+++++++++++++","++++++++++++++++++","+++++++++","+++++++++","++++++++++++++","+++++++++++++","+++++++++++++++++++","+++++++++++++++++++"',
    '"GENE SYMBOL","GENE ID (HGNC)","DISEASE LABEL","DISEASE ID (MONDO)","MOI","SOP","CLASSIFICATION","ONLINE REPORT","CLASSIFICATION DATE","GCEP"',
    '"+++++++++++","++++++++++++++","+++++++++++++","++++++++++++++++++","+++++++++","+++++++++","++++++++++++++","+++++++++++++","+++++++++++++++++++","+++++++++++++++++++"',
]


def _curation_line(symbol, hgnc_id, label, mondo, moi, classification):
    """Return a ClinGen gene-disease validity data line."""
    return (
        f'"{symbol}","HGNC:{hgnc_id}","{label}","{mondo}","{moi}","SOP7","{classification}",'
        f'"https://search.clinicalgenome.org/kb/gene-validity/CGGV:assertion_{symbol}",'
        '"2020-07-10T16:00:00.000Z","Some Gene Curation Expert Panel"'
    )


def test_parse_clingen_gene_validity_csv():
    """Test parsing ClinGen gene-disease validity data lines, skipping the header block."""
    # GIVEN a ClinGen gene validity file with a header and a line with a quoted comma
    lines = HEADER + [
        _curation_line(
            "ADA",
            186,
            "severe combined immunodeficiency, autosomal recessive",
            "MONDO:0007064",
            "AR",
            "Definitive",
        )
    ]
    # WHEN parsing it
    curations = parse_clingen_gene_validity_csv(lines)
    # THEN only the data line is returned, with the comma kept in the label
    assert len(curations) == 1
    assert curations[0]["hgnc_id"] == "HGNC:186"
    assert curations[0]["description"] == "severe combined immunodeficiency, autosomal recessive"
    assert curations[0]["inheritance"] == "AR"
    assert curations[0]["classification"] == "Definitive"


def test_get_clingen_disease_terms_multiple_genes():
    """Test that curations of several genes for one MONDO term are pooled into one disease term."""
    # GIVEN two genes curated for the same disease
    lines = HEADER + [
        _curation_line("ABCG5", 13886, "sitosterolemia", "MONDO:0008863", "AR", "Definitive"),
        _curation_line("ABCG8", 13887, "sitosterolemia", "MONDO:0008863", "AR", "Moderate"),
    ]
    # WHEN collecting disease terms
    terms = get_clingen_disease_terms(lines)
    # THEN one MONDO term holds both genes and their curations
    term = terms["MONDO:0008863"]
    assert term["description"] == "sitosterolemia"
    assert term["hgnc_ids"] == {13886, 13887}
    assert term["inheritance"] == {"AR"}
    assert {
        (curation["hgnc_symbol"], curation["classification"])
        for curation in term["clingen_gene_validity"]
    } == {("ABCG5", "Definitive"), ("ABCG8", "Moderate")}


def test_get_clingen_disease_terms_skips_non_supportive():
    """Test that disputed, refuted and no known relationship curations do not link genes to diseases."""
    # GIVEN a disease with one supportive and three non-supportive curations
    lines = HEADER + [
        _curation_line("KCNQ1", 6294, "long QT syndrome", "MONDO:0002442", "AD", "Definitive"),
        _curation_line("AKAP9", 379, "long QT syndrome", "MONDO:0002442", "AD", "Disputed"),
        _curation_line("ANK2", 493, "long QT syndrome", "MONDO:0002442", "AD", "Refuted"),
        _curation_line(
            "GENE1", 1, "some disease", "MONDO:0000001", "AR", "No Known Disease Relationship"
        ),
    ]
    # WHEN collecting disease terms
    terms = get_clingen_disease_terms(lines)
    # THEN only the supportive curation is kept
    assert terms["MONDO:0002442"]["hgnc_ids"] == {6294}
    assert len(terms["MONDO:0002442"]["clingen_gene_validity"]) == 1
    # THEN a disease with only non-supportive curations is not added
    assert "MONDO:0000001" not in terms


def test_get_clingen_disease_terms_demo_file(clingen_disease_lines):
    """Test collecting disease terms from the demo ClinGen gene validity file."""
    # WHEN collecting disease terms from the demo file
    terms = get_clingen_disease_terms(clingen_disease_lines)
    # THEN MONDO terms are returned
    assert terms
    assert all(disease_id.startswith("MONDO:") for disease_id in terms)
    assert terms["MONDO:0018544"]["hgnc_ids"] == {61}
