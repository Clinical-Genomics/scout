# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_view_transcripts(mock_app):
    """Test CLI that shows all transcripts in the database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI without arguments
    result = runner.invoke(cli, ["view", "transcripts"])
    assert result.exit_code == 0
    # cli should return just header, since there are no transcripts in database
    assert "Chromosome\tstart\tend\ttranscript_id\thgnc_id\trefseq\tis_primary" in result.output

    # insert one transcript into database
    transcript_obj = {
        "ensembl_transcript_id": "ENST00000367019",
        "hgnc_id": 23143,
        "chrom": "1",
        "start": 210111576,
        "end": 210335568,
        "is_primary": False,
        "build": "37",
        "length": 223992,
    }
    assert store.transcript_collection.insert_one(transcript_obj)
    assert sum(1 for i in store.transcript_collection.find()) == 1

    # Test again the CLI
    result = runner.invoke(cli, ["view", "transcripts"])
    assert result.exit_code == 0
    # and it should return the transcript
    assert "1\t210111576\t210335568\tENST00000367019\t23143" in result.output

    # Test again the CLI with gene option
    result = runner.invoke(cli, ["view", "transcripts", "-i", 23143])
    assert result.exit_code == 0
    # and it should return the transcript
    assert "1\t210111576\t210335568\tENST00000367019\t23143" in result.output

    # Test again the CLI with a non valid hgnc_id
    result = runner.invoke(cli, ["view", "transcripts", "-i", 777887])
    assert result.exit_code == 0
    # and transcript data is not found
    assert "1\t210111576\t210335568\tENST00000367019\t23143" not in result.output

    # Test  the CLI with another build
    result = runner.invoke(cli, ["view", "transcripts", "-b", "38"])
    assert result.exit_code == 0
    # and transcript data is not found
    assert "1\t210111576\t210335568\tENST00000367019\t23143" not in result.output

    # Test the CLI with json flag
    result = runner.invoke(cli, ["view", "transcripts", "--json"])
    assert result.exit_code == 0
    # and transcript data is not found
    assert "transcript_id': 'ENST00000367019'" in result.output
