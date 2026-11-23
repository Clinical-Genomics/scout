import responses

from scout.utils.hgvs import (
    VALIDATOR_URL,
    get_brief_hgvs,
    get_representative_transcript,
    transcript_hgvs,
    validate_hgvs,
)


@responses.activate
def test_validate_hgvs_failed():
    """Test the API that validates a variant descriptor when the descriptor is NOT valid"""

    # GIVEN a variant descriptor expression
    desc = "NM_001145436.2:c.1840C>T"
    build = "GRCh37"

    # GIVEN a mocked warning (failed validation) response from the VariantValidator API
    resp_content = {
        "flag": "warning",
        "validation_warnings": [
            "NM_001145436.2:c.1840C>T: Variant reference (C) does not agree with reference sequence (G)"
        ],
    }
    responses.add(
        responses.GET,
        VALIDATOR_URL.format(build, desc),
        json=resp_content,
        status=200,
    )
    # THEN validation should fail
    assert validate_hgvs(build, desc) is False


@responses.activate
def test_validate_hgvs_success():
    """Test the API that validates a variant descriptor when the descriptor is valid"""

    # GIVEN a variant descriptor expression
    desc = "NM_001145437.2:c.1600C>T"
    build = "GRCh37"

    # GIVEN a mocked success response from the VariantValidator API
    resp_content = {"flag": "gene_variant"}
    responses.add(
        responses.GET,
        VALIDATOR_URL.format(build, desc),
        json=resp_content,
        status=200,
    )
    # THEN validation should return True
    assert validate_hgvs(build, desc)


CANONICAL_TX = {
    "transcript_id": "ENST00000001",
    "is_canonical": True,
    "coding_sequence_name": "c.100A>G",
    "functional_annotations": ["missense_variant"],
}
PRIMARY_TX = {
    "transcript_id": "ENST00000002",
    "is_primary": True,
    "refseq_id": "NM_000002",
    "coding_sequence_name": "c.200A>G",
}
MANE_TX = {
    "transcript_id": "ENST00000003",
    "refseq_id": "NM_003002",
    "mane_select_transcript": "NM_003002.4",
    "coding_sequence_name": "c.274G>T",
    "protein_sequence_name": "p.Asp92Tyr",
    "functional_annotations": ["missense_variant"],
    "exon": "3/4",
}
DISEASE_ASSOCIATED_TX = {
    "transcript_id": "ENST00000004",
    "refseq_id": "NM_000004",
    "is_disease_associated": True,
    "coding_sequence_name": "c.400A>G",
}


def test_get_representative_transcript_priority():
    """Test the representative transcript priority order."""
    # GIVEN a gene with canonical, primary, MANE and panel disease associated transcripts
    transcripts = [CANONICAL_TX, PRIMARY_TX, MANE_TX, DISEASE_ASSOCIATED_TX]

    # THEN the panel disease associated transcript is preferred
    assert get_representative_transcript({"transcripts": transcripts}) == DISEASE_ASSOCIATED_TX
    # THEN followed by MANE, HGNC primary and VEP canonical
    assert get_representative_transcript({"transcripts": transcripts[:3]}) == MANE_TX
    assert get_representative_transcript({"transcripts": transcripts[:2]}) == PRIMARY_TX
    assert get_representative_transcript({"transcripts": transcripts[:1]}) == CANONICAL_TX


def test_get_representative_transcript_no_transcripts():
    """Test that a gene without transcripts has no representative transcript."""
    assert get_representative_transcript({}) is None


def test_get_brief_hgvs():
    """Test that protein altering variants are briefly described by p., others by c."""
    # GIVEN a missense variant with both c. and p.
    # THEN p. is used
    assert get_brief_hgvs(MANE_TX) == "p.Asp92Tyr"

    # GIVEN a synonymous variant, with an URL encoded p.
    synonymous = {
        "coding_sequence_name": "c.276C>T",
        "protein_sequence_name": "p.Asp92%3D",
        "functional_annotations": ["synonymous_variant"],
    }
    # THEN c. is used
    assert get_brief_hgvs(synonymous) == "c.276C>T"

    # GIVEN a missense variant without p. THEN c. is used
    assert get_brief_hgvs(CANONICAL_TX) == "c.100A>G"


def test_transcript_hgvs_mane():
    """Test that a MANE transcript uses its RefSeq accession as HGVS reference."""
    hgvs = transcript_hgvs(MANE_TX)

    assert hgvs["hgvs_reference"] == "NM_003002.4"
    assert hgvs["hgvs_c_full"] == "NM_003002.4:c.274G>T"
    assert hgvs["selection_reason"] == "MANE Select"
    assert hgvs["exon"] == "3/4"


def test_transcript_hgvs_non_mane():
    """Test that HGVS for a non-MANE transcript keeps the annotated transcript as reference."""
    # GIVEN an Ensembl transcript matched to a RefSeq transcript, but not MANE
    hgvs = transcript_hgvs(PRIMARY_TX)

    # THEN the HGVS is not transferred to the RefSeq accession
    assert hgvs["hgvs_reference"] == "ENST00000002"
    assert hgvs["hgvs_c_full"] == "ENST00000002:c.200A>G"
    assert hgvs["refseq_id"] == "NM_000002"
