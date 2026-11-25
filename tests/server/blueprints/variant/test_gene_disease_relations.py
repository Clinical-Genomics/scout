"""Tests for the gene-disease relations macros on the variant page"""

CLINGEN_TERM = {
    "_id": "MONDO:0018544",
    "source": "MONDO",
    "description": "adrenoleukodystrophy",
    "disease_link": "https://search.clinicalgenome.org/kb/conditions/MONDO:0018544",
    "inheritance": ["XL"],
    "clingen_gene_validity": [
        {"hgnc_id": 61, "hgnc_symbol": "ABCD1", "inheritance": "XL", "classification": "Definitive"}
    ],
}


def _render_disease_card(app, variant: dict) -> str:
    """Render the variant page disease card for a variant."""
    with app.test_request_context():
        macros = app.jinja_env.get_template("variant/gene_disease_relations.html").module
        return str(macros.orpha_omim_phenotypes(variant))


def test_disease_card_only_clingen(app):
    """Test that only the ClinGen table is shown when the gene has only ClinGen terms."""
    # GIVEN a variant gene with only a ClinGen MONDO disease term
    variant = {
        "genes": [
            {"hgnc_id": 61, "common": {"hgnc_symbol": "ABCD1"}, "disease_terms": [CLINGEN_TERM]}
        ]
    }
    # WHEN rendering the disease card
    html = _render_disease_card(app, variant)
    # THEN the ClinGen table is shown, with the curation
    assert "Table of ClinGen gene-disease validity curations" in html
    assert "Definitive" in html
    # THEN the lower case MONDO label is shown with a capital first letter
    assert "Adrenoleukodystrophy" in html
    # THEN the empty OMIM and ORPHA tables are not
    assert "OMIM Phenotype" not in html
    assert "ORPHA Phenotype" not in html


def test_disease_card_clingen_other_gene(app):
    """Test that a ClinGen term curated for another gene of the disease gives no table."""
    # GIVEN a variant gene linked to a ClinGen term through a curation of another gene
    variant = {
        "genes": [
            {"hgnc_id": 1, "common": {"hgnc_symbol": "GENE1"}, "disease_terms": [CLINGEN_TERM]}
        ]
    }
    # WHEN rendering the disease card
    html = _render_disease_card(app, variant)
    # THEN no disease tables are shown
    assert "Table of ClinGen gene-disease validity curations" not in html
    assert "No associated diseases" in html


def test_disease_card_omim(app):
    """Test that the OMIM table is shown for OMIM terms, without the other tables."""
    # GIVEN a variant gene with an OMIM disease term
    omim_term = {
        "_id": "OMIM:300100",
        "source": "OMIM",
        "description": "Adrenoleukodystrophy",
        "inheritance": ["XR"],
    }
    variant = {
        "genes": [
            {
                "hgnc_id": 61,
                "common": {"hgnc_symbol": "ABCD1", "omim_id": 300371},
                "disease_terms": [omim_term],
            }
        ]
    }
    # WHEN rendering the disease card
    html = _render_disease_card(app, variant)
    # THEN only the OMIM table is shown
    assert "OMIM Phenotype" in html
    assert "ORPHA Phenotype" not in html
    assert "Table of ClinGen gene-disease validity curations" not in html
