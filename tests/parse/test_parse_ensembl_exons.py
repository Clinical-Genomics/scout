from scout.parse.ensembl import parse_ensembl_exons

from scout.constants import CHROMOSOMES


def test_exons_file_37(exons_handle):
    """This test exists to make sure that the demo exons file is on correct format"""
    # GIVEN the path to an ensembl formated exons file

    # WHEN parsing the lines
    header = next(exons_handle).rstrip().split("\t")

    ## THEN assert that the information is on correct format
    for exon_line in exons_handle:
        exon_line = exon_line.rstrip().split("\t")
        exon_info = dict(zip(header, exon_line))
        assert exon_info["Chromosome/scaffold name"] in CHROMOSOMES
        assert exon_info["Exon stable ID"].startswith("ENSE")
        assert exon_info["Gene stable ID"].startswith("ENSG")
        assert exon_info["Transcript stable ID"].startswith("ENST")

        assert int(exon_info["Exon region start (bp)"])
        assert int(exon_info["Exon region end (bp)"])


def test_exons_file_38(exons_38_handle):
    """This test exists to make sure that the demo exons file is on correct format"""
    # GIVEN the path to an ensembl formated exons file

    # WHEN parsing the lines
    header = next(exons_38_handle).rstrip().split("\t")

    ## THEN assert that the information is on correct format
    for exon_line in exons_38_handle:
        exon_line = exon_line.rstrip().split("\t")
        exon_info = dict(zip(header, exon_line))
        assert exon_info["Chromosome/scaffold name"] in CHROMOSOMES
        assert exon_info["Exon stable ID"].startswith("ENSE")
        assert exon_info["Gene stable ID"].startswith("ENSG")
        assert exon_info["Transcript stable ID"].startswith("ENST")

        assert int(exon_info["Exon region start (bp)"])
        assert int(exon_info["Exon region end (bp)"])


def test_parse_ensembl_exons(exons_handle):
    """Test to parse a small dataframe line of ensembl transcript"""
    ## GIVEN a iterable with exon information from ensembl

    ## WHEN parsing the exons
    parsed_exons = parse_ensembl_exons(exons_handle)
    parsed_exon = next(parsed_exons)

    ## THEN assert the parsed transcript is as expected
    assert parsed_exon["chrom"]
    assert parsed_exon["gene"]
    assert parsed_exon["transcript"]


def test_parse_ensembl_exons_iterable():
    """Test to parse all ensembl exons"""
    ## GIVEN an iterable with ensembl exon data
    exons_handle = [
        "Chromosome/scaffold name\tGene stable ID\tTranscript stable ID\tExon stable ID\tExon"
        " region start (bp)\tExon region end (bp)\t5' UTR start\t5' UTR end\t3' UTR start\t3'"
        " UTR end\tStrand\tExon rank in transcript",
        "1\tENSG00000176022\tENST00000379198\tENSE00001439793\t1167629\t1170421\t1167629\t1"
        "167658\t1168649\t1170421\t1\t1",
    ]
    ## WHEN parsing the exons in that file
    exons = parse_ensembl_exons(exons_handle)
    parsed_exon = next(exons)

    ## THEN assert that the exon is correctly parsed
    assert parsed_exon["chrom"] == "1"
    assert parsed_exon["ens_exon_id"] == "ENSE00001439793"
    assert parsed_exon["transcript"] == "ENST00000379198"
    assert parsed_exon["gene"] == "ENSG00000176022"
    assert parsed_exon["exon_chrom_start"] == 1167629
    assert parsed_exon["exon_chrom_end"] == 1170421
    assert parsed_exon["5_utr_start"] == 1167629
    assert parsed_exon["5_utr_end"] == 1167658
    assert parsed_exon["3_utr_start"] == 1168649
    assert parsed_exon["3_utr_end"] == 1170421
    assert parsed_exon["rank"] == 1
    assert parsed_exon["strand"] == 1
    ## THEN assert start is max(5_utr_end, exon_chrom_start) since strand is 1
    assert parsed_exon["start"] == 1167658
    ## THEN assert end is min(3_utr_start, exon_chrom_end) since strand is 1
    assert parsed_exon["end"] == 1168649


def test_parse_ensembl_exons_missing_five_utr_start():
    """Test to parse all ensembl exons"""
    ## GIVEN an iterable with ensembl exon data
    exons_handle = [
        "Chromosome/scaffold name\tGene stable ID\tTranscript stable ID\tExon stable ID\tExon"
        " region start (bp)\tExon region end (bp)\t5' UTR start\t5' UTR end\t3' UTR start\t3'"
        " UTR end\tStrand\tExon rank in transcript",
        "1\tENSG00000176022\tENST00000379198\tENSE00001439793\t1167629\t1170421\t\t1"
        "167658\t1168649\t1170421\t1\t1",
    ]
    ## WHEN parsing the exons in that file
    exons = parse_ensembl_exons(exons_handle)
    parsed_exon = next(exons)

    ## THEN assert that the exon is correctly parsed
    assert parsed_exon["chrom"] == "1"
    assert parsed_exon["ens_exon_id"] == "ENSE00001439793"
    assert parsed_exon["transcript"] == "ENST00000379198"
    assert parsed_exon["gene"] == "ENSG00000176022"
    assert parsed_exon["5_utr_start"] is None


def test_parse_ensembl_exons_missing_five_utr_end():
    """Test to parse all ensembl exons"""
    ## GIVEN an iterable with ensembl exon data
    exons_handle = [
        "Chromosome/scaffold name\tGene stable ID\tTranscript stable ID\tExon stable ID\tExon"
        " region start (bp)\tExon region end (bp)\t5' UTR start\t5' UTR end\t3' UTR start\t3'"
        " UTR end\tStrand\tExon rank in transcript",
        "1\tENSG00000176022\tENST00000379198\tENSE00001439793\t1167629\t1170421\t\t"
        "\t1168649\t1170421\t1\t1",
    ]
    ## WHEN parsing the exons in that file
    exons = parse_ensembl_exons(exons_handle)
    parsed_exon = next(exons)

    ## THEN assert that the exon is correctly parsed
    assert parsed_exon["chrom"] == "1"
    assert parsed_exon["ens_exon_id"] == "ENSE00001439793"
    assert parsed_exon["transcript"] == "ENST00000379198"
    assert parsed_exon["gene"] == "ENSG00000176022"
    assert parsed_exon["5_utr_start"] is None
    assert parsed_exon["5_utr_end"] is None


def test_parse_ensembl_exons_missing_three_utr_start():
    """Test to parse all ensembl exons"""
    ## GIVEN an iterable with ensembl exon data
    exons_handle = [
        "Chromosome/scaffold name\tGene stable ID\tTranscript stable ID\tExon stable ID\tExon"
        " region start (bp)\tExon region end (bp)\t5' UTR start\t5' UTR end\t3' UTR start\t3'"
        " UTR end\tStrand\tExon rank in transcript",
        "1\tENSG00000176022\tENST00000379198\tENSE00001439793\t1167629\t1170421\t\t"
        "\t\t1170421\t1\t1",
    ]
    ## WHEN parsing the exons in that file
    exons = parse_ensembl_exons(exons_handle)
    parsed_exon = next(exons)

    ## THEN assert that the exon is correctly parsed
    assert parsed_exon["chrom"] == "1"
    assert parsed_exon["ens_exon_id"] == "ENSE00001439793"
    assert parsed_exon["transcript"] == "ENST00000379198"
    assert parsed_exon["gene"] == "ENSG00000176022"
    assert parsed_exon["5_utr_start"] is None
    assert parsed_exon["5_utr_end"] is None
    assert parsed_exon["3_utr_start"] is None


def test_parse_ensembl_exons_missing_three_utr_end():
    """Test to parse all ensembl exons"""
    ## GIVEN an iterable with ensembl exon data
    exons_handle = [
        "Chromosome/scaffold name\tGene stable ID\tTranscript stable ID\tExon stable ID\tExon"
        " region start (bp)\tExon region end (bp)\t5' UTR start\t5' UTR end\t3' UTR start\t3'"
        " UTR end\tStrand\tExon rank in transcript",
        "1\tENSG00000176022\tENST00000379198\tENSE00001439793\t1167629\t1170421\t\t" "\t\t\t1\t1",
    ]
    ## WHEN parsing the exons in that file
    exons = parse_ensembl_exons(exons_handle)
    parsed_exon = next(exons)

    ## THEN assert that the exon is correctly parsed
    assert parsed_exon["chrom"] == "1"
    assert parsed_exon["ens_exon_id"] == "ENSE00001439793"
    assert parsed_exon["transcript"] == "ENST00000379198"
    assert parsed_exon["gene"] == "ENSG00000176022"
    assert parsed_exon["5_utr_start"] is None
    assert parsed_exon["5_utr_end"] is None
    assert parsed_exon["3_utr_start"] is None
    assert parsed_exon["3_utr_end"] is None
