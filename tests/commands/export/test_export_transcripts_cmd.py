# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_export_transcripts(mock_app):
    """Test the CLI command that exports transcripts"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Database should have an empty transcript collection
    assert store.transcript_collection.find_one() is None

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

    # Test the export panel cli without passing any data (default will be build 38)
    result = runner.invoke(cli, ["export", "transcripts"])

    # The commannd should return the transcript
    assert result.exit_code == 0
    assert transcript_obj["ensembl_transcript_id"] in result.output

    # Test the export panel cli by passing chromosome buil 38
    result = runner.invoke(cli, ["export", "transcripts", "-b", "38"])

    # The commannd should NOT return the transcript
    assert result.exit_code == 0
    assert transcript_obj["ensembl_transcript_id"] not in result.output

    # Test the export panel cli by passing chromosome buil 37 (same as in transcript_obj)
    result = runner.invoke(cli, ["export", "transcripts", "-b", "37"])

    # The commannd should return the transcript
    assert result.exit_code == 0
    assert transcript_obj["ensembl_transcript_id"] in result.output
