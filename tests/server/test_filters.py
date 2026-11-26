"""Tests for the Scout template filters"""

from scout.server.filters import pretty_variant


def test_pretty_variant_snv_brief_hgvs():
    """Test that a SNV is briefly displayed by gene and p. for a protein altering variant."""
    # GIVEN a missense SNV with c. and p. on its canonical transcript
    variant = {
        "category": "snv",
        "genes": [
            {
                "hgnc_id": 1,
                "hgnc_symbol": "POT1",
                "hgvs_identifier": "c.274G>T",
                "transcripts": [
                    {
                        "transcript_id": "ENST1",
                        "is_canonical": True,
                        "coding_sequence_name": "c.274G>T",
                        "protein_sequence_name": "p.Asp92Tyr",
                        "functional_annotations": ["missense_variant"],
                    }
                ],
            }
        ],
    }
    # THEN the protein change is shown
    assert pretty_variant(variant) == "POT1 p.Asp92Tyr"


def test_pretty_variant_snv_without_transcripts():
    """Test that a SNV gene without transcripts falls back to the gene HGVS identifier."""
    variant = {
        "category": "snv",
        "genes": [{"hgnc_id": 1, "hgnc_symbol": "POT1", "hgvs_identifier": "c.274G>T"}],
    }
    assert pretty_variant(variant) == "POT1 c.274G>T"


def test_pretty_variant_str_repid():
    """Test that an STR is described by its repeat id and motif count."""
    # GIVEN an STR with a repeat id, a motif count and a gene
    variant = {
        "category": "str",
        "str_repid": "ATXN1",
        "str_mc": 45,
        "alternative": "<STR45>",
        "genes": [{"hgnc_id": 10548, "hgnc_symbol": "ATXN1"}],
    }
    # THEN the repeat id is used, with the motif count
    assert pretty_variant(variant) == "ATXN1 STR45"


def test_pretty_variant_str_gene_symbol_fallback():
    """Test that an STR without repeat or locus id falls back to its gene symbols."""
    # GIVEN an STR with neither str_repid nor str_trid, with variant genes (hgnc_symbol),
    # a gene with only an id, and a gene with a symbol key
    variant = {
        "category": "str",
        "str_mc": 45,
        "alternative": "<STR45>",
        "genes": [
            {"hgnc_id": 10548, "hgnc_symbol": "ATXN1"},
            {"hgnc_id": 1},
            {"hgnc_id": 2, "symbol": "GENE2"},
        ],
    }
    # THEN the available gene symbols are shown, without blanks for genes lacking one
    assert pretty_variant(variant) == "ATXN1 GENE2 STR45"


def test_pretty_variant_str_no_names():
    """Test that an STR without repeat id or gene symbols is described by its motif count."""
    # GIVEN an STR with no repeat id and no genes
    variant = {"category": "str", "str_mc": 45, "alternative": "<STR45>"}
    # THEN only the motif count is shown
    assert pretty_variant(variant) == "STR45"
