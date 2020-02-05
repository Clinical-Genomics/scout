from scout.parse.ensembl import (
    parse_ensembl_line,
    parse_ensembl_transcripts,
    parse_transcripts,
)


def test_parse_ensembl_line(transcript_info):
    """Test to parse a line of ensembl transcript"""
    ## GIVEN some transcript information and a header
    header = [
        "Chromosome/scaffold name",
        "Gene stable ID",
        "Transcript stable ID",
        "Transcript start (bp)",
        "Transcript end (bp)",
        "RefSeq mRNA ID",
        "RefSeq mRNA predicted ID",
        "RefSeq ncRNA ID",
    ]

    transcript_line = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(
        transcript_info["chrom"],
        transcript_info["ens_gene_id"],
        transcript_info["ens_transcript_id"],
        transcript_info["start"],
        transcript_info["end"],
        transcript_info["refseq_mrna"],
        transcript_info["refseq_mrna_pred"],
        transcript_info["refseq_ncrna"],
    )

    ## WHEN parsing the transcript line
    parsed_transcript = parse_ensembl_line(header=header, line=transcript_line)

    ## THEN assert the parsed transcript is as expected
    assert parsed_transcript["chrom"] == transcript_info["chrom"]
    assert parsed_transcript["ensembl_gene_id"] == transcript_info["ens_gene_id"]
    assert (
        parsed_transcript["ensembl_transcript_id"]
        == transcript_info["ens_transcript_id"]
    )
    assert parsed_transcript["transcript_start"] == transcript_info["start"]
    assert parsed_transcript["transcript_end"] == transcript_info["end"]
    assert parsed_transcript["refseq_mrna"] == transcript_info["refseq_mrna"]
    assert "refseq_mrna_predicted" not in parsed_transcript
    assert "refseq_ncrna" not in parsed_transcript


def test_parse_ensembl_transcripts(transcripts_handle):
    """Test to parse all ensembl transcripts"""
    transcripts = parse_ensembl_transcripts(transcripts_handle)

    for transcript in transcripts:
        assert transcript["ensembl_transcript_id"]
        assert transcript["ensembl_gene_id"]


def test_parse_transcripts_file(transcripts_handle):
    """Test to parse all ensembl transcripts"""
    transcripts = parse_transcripts(transcripts_handle)

    for transcript_id in transcripts:
        transcript = transcripts[transcript_id]
        assert transcript["ensembl_transcript_id"]
        assert transcript["ensembl_gene_id"]
