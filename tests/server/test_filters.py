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
