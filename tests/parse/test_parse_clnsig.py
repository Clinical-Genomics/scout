from pprint import pprint as pp

from scout.parse.variant import parse_variant
from scout.parse.variant.clnsig import is_pathogenic, parse_clnsig


def test_parse_classic_clnsig(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "RCV000014440.17|RCV000014441.25|RCV000014442.25|RCV000014443.17|RCV000184011.1|RCV000188658.1"
    clnsig = "5|4|3|2|1|0"
    revstat = "conf|single|single|single|conf|conf"

    cyvcf2_variant.INFO["CLNACC"] = acc_nr
    cyvcf2_variant.INFO["CLNSIG"] = clnsig
    cyvcf2_variant.INFO["CLNREVSTAT"] = revstat

    ## WHEN parsing the annotations
    clnsig_annotations = parse_clnsig(cyvcf2_variant)

    ## THEN assert that they where parsed correct
    assert len(clnsig_annotations) == len(clnsig.split("|"))

    ## THEN assert that all accessions are there
    assert {term["accession"] for term in clnsig_annotations} == set(acc_nr.split("|"))
    ## THEN assert that all have been parsed as expected
    for entry in clnsig_annotations:
        if entry["accession"] == "RCV000014440.17":
            assert entry["value"] == 5
            assert entry["revstat"] == "conf"

        if entry["accession"] == "RCV000014441.25":
            assert entry["value"] == 4
            assert entry["revstat"] == "single"

        if entry["accession"] == "RCV000014442.25":
            assert entry["value"] == 3
            assert entry["revstat"] == "single"

        if entry["accession"] == "RCV000014443.17":
            assert entry["value"] == 2
            assert entry["revstat"] == "single"

        if entry["accession"] == "RCV000184011.1":
            assert entry["value"] == 1
            assert entry["revstat"] == "conf"

        if entry["accession"] == "RCV000188658.1":
            assert entry["value"] == 0
            assert entry["revstat"] == "conf"


def test_parse_modern_clnsig(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "265359"
    clnsig = "Pathogenic/Likely_pathogenic"
    revstat = "criteria_provided,_multiple_submitters,_no_conflicts"

    cyvcf2_variant.INFO["CLNACC"] = acc_nr
    cyvcf2_variant.INFO["CLNSIG"] = clnsig
    cyvcf2_variant.INFO["CLNREVSTAT"] = revstat

    ## WHEN parsing the annotations
    clnsig_annotations = parse_clnsig(cyvcf2_variant)

    ## THEN assert that the correct terms are parsed
    assert set(["pathogenic", "likely_pathogenic"]) == {
        term["value"] for term in clnsig_annotations
    }
    ## THEN assert that they where parsed correct
    assert len(clnsig_annotations) == len(clnsig.split("/"))


def test_parse_modern_clnsig_clnvid(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "10"
    clnsig = "conflicting_interpretations_of_pathogenicity&_other"
    revstat = "criteria_provided&_conflicting_interpretations"

    cyvcf2_variant.INFO["CLNVID"] = acc_nr
    cyvcf2_variant.INFO["CLNSIG"] = clnsig
    cyvcf2_variant.INFO["CLNREVSTAT"] = revstat

    ## WHEN parsing the annotations
    clnsig_annotations = parse_clnsig(cyvcf2_variant)

    ## THEN assert that the correct terms are parsed
    assert set(["conflicting_interpretations_of_pathogenicity", "other"]) == {
        term["value"] for term in clnsig_annotations
    }
    ## THEN assert that they where parsed correct
    assert len(clnsig_annotations) == 2


def test_parse_semi_modern_clnsig(cyvcf2_variant):
    ## GIVEN a variant with semi modern clinvar annotations
    # This means that there can be spaces between words
    acc_nr = "265359"
    clnsig = "Pathogenic/Likely pathogenic"
    revstat = "criteria_provided,_multiple_submitters,_no_conflicts"

    cyvcf2_variant.INFO["CLNACC"] = acc_nr
    cyvcf2_variant.INFO["CLNSIG"] = clnsig
    cyvcf2_variant.INFO["CLNREVSTAT"] = revstat

    ## WHEN parsing the annotations
    clnsig_annotations = parse_clnsig(cyvcf2_variant)

    ## THEN assert that the correct terms are parsed
    assert set(["pathogenic", "likely_pathogenic"]) == {
        term["value"] for term in clnsig_annotations
    }
    ## THEN assert that they where parsed correct
    assert len(clnsig_annotations) == len(clnsig.split("/"))
    for annotation in clnsig_annotations:
        assert annotation["accession"] == int(acc_nr)
        assert set(annotation["revstat"].split(",")) == set(
            ["criteria_provided", "multiple_submitters", "no_conflicts"]
        )


def test_parse_clnsig_all(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "265359"
    clnsig = "Pathogenic/Likely pathogenic"
    revstat = "criteria_provided,_multiple_submitters,_no_conflicts"

    cyvcf2_variant.INFO["CLNACC"] = acc_nr
    cyvcf2_variant.INFO["CLNSIG"] = clnsig
    cyvcf2_variant.INFO["CLNREVSTAT"] = revstat

    revstat_groups = [rev.lstrip("_") for rev in revstat.split(",")]

    clnsig_annotations = parse_clnsig(cyvcf2_variant)

    ## assert that they where parsed correct
    assert len(clnsig_annotations) == 2

    for entry in clnsig_annotations:
        assert entry["accession"] == int(acc_nr)
        assert entry["value"] in ["pathogenic", "likely_pathogenic"]
        assert entry["revstat"] == ",".join(revstat_groups)


def test_parse_complex_clnsig(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "265359"
    clnsig = "Benign/Likely_benign,_other"
    revstat = "criteria_provided,_multiple_submitters,_no_conflicts"

    cyvcf2_variant.INFO["CLNACC"] = acc_nr
    cyvcf2_variant.INFO["CLNSIG"] = clnsig
    cyvcf2_variant.INFO["CLNREVSTAT"] = revstat

    ## WHEN parsing the annotations
    clnsig_annotations = parse_clnsig(cyvcf2_variant)

    ## THEN assert that they where parsed correct
    assert len(clnsig_annotations) == 3


def test_parse_clnsig_transcripts(cyvcf2_variant):
    ## GIVEN a variant with slash-separated values or values that start with underscore
    transcripts = [
        {"clnsig": ["pathogenic/likely_pathogenic", "likely_pathogenic", "pathogenic", "_other"]}
    ]

    ## WHEN parsing the annotations
    clnsig_annotations = parse_clnsig(cyvcf2_variant, transcripts=transcripts)

    ## THEN assert that they where parsed correct
    assert len(clnsig_annotations) == 3
    for clnsig in ["pathogenic", "likely_pathogenic", "other"]:
        clnsig_dict = {"value": clnsig}
        assert clnsig_dict in clnsig_annotations


def test_is_pathogenic_pathogenic(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "265359"
    clnsig = "Pathogenic"
    revstat = "criteria_provided,_multiple_submitters,_no_conflicts"

    cyvcf2_variant.INFO["CLNVID"] = acc_nr
    cyvcf2_variant.INFO["CLNSIG"] = clnsig
    cyvcf2_variant.INFO["CLNREVSTAT"] = revstat

    ## WHEN checking if variants should be loaded
    pathogenic = is_pathogenic(cyvcf2_variant)

    ## THEN assert that The variant should be loaded
    assert pathogenic is True


def test_is_pathogenic_classic_pathogenic(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "RCV000014440.17|RCV000014441.25|RCV000014442.25|RCV000014443.17|RCV000184011.1|RCV000188658.1"
    clnsig = "5|4|3|2|1|0"
    revstat = "conf|single|single|single|conf|conf"

    cyvcf2_variant.INFO["CLNVID"] = acc_nr
    cyvcf2_variant.INFO["CLNSIG"] = clnsig
    cyvcf2_variant.INFO["CLNREVSTAT"] = revstat

    ## WHEN checking if variants should be loaded
    pathogenic = is_pathogenic(cyvcf2_variant)

    ## THEN assert that The variant should be loaded
    assert pathogenic is True


def test_is_pathogenic_benign(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "265359"
    clnsig = "Likely_benign"
    revstat = "criteria_provided,_multiple_submitters,_no_conflicts"

    cyvcf2_variant.INFO["CLNVID"] = acc_nr
    cyvcf2_variant.INFO["CLNSIG"] = clnsig
    cyvcf2_variant.INFO["CLNREVSTAT"] = revstat

    ## WHEN checking if variants should be loaded
    pathogenic = is_pathogenic(cyvcf2_variant)

    ## THEN assert that The variant should be loaded
    assert pathogenic is False


def test_is_pathogenic_no_annotation(cyvcf2_variant):
    ## GIVEN a variant without clinvar annotations

    ## WHEN checking if variants should be loaded
    pathogenic = is_pathogenic(cyvcf2_variant)

    ## THEN assert that The variant should be loaded
    assert pathogenic is False


def test_is_pathogenic_VEP97_conflicting(one_vep97_annotated_variant):

    ## WHEN checking if variants should be loaded
    pathogenic = is_pathogenic(one_vep97_annotated_variant)

    ## THEN assert that the variant should be loaded
    assert pathogenic is True


def test_parse_clinsig_vep97(one_vep97_annotated_variant, real_populated_database, case_obj):
    """Test Clinsig parsing in a VEP97 formatted VCF"""

    # GIVEN a variant annotated using the following CSQ entry fields
    csq_header = "Allele|Consequence|IMPACT|SYMBOL|Gene|Feature_type|Feature|BIOTYPE|EXON|INTRON|HGVSc|HGVSp|cDNA_position|CDS_position|Protein_position|Amino_acids|Codons|Existing_variation|DISTANCE|STRAND|FLAGS|SYMBOL_SOURCE|HGNC_ID|CANONICAL|TSL|APPRIS|CCDS|ENSP|SWISSPROT|TREMBL|UNIPARC|REFSEQ_MATCH|SOURCE|GIVEN_REF|USED_REF|BAM_EDIT|SIFT|PolyPhen|DOMAINS|HGVS_OFFSET|MOTIF_NAME|MOTIF_POS|HIGH_INF_POS|MOTIF_SCORE_CHANGE|MES-NCSS_downstream_acceptor|MES-NCSS_downstream_donor|MES-NCSS_upstream_acceptor|MES-NCSS_upstream_donor|MES-SWA_acceptor_alt|MES-SWA_acceptor_diff|MES-SWA_acceptor_ref|MES-SWA_acceptor_ref_comp|MES-SWA_donor_alt|MES-SWA_donor_diff|MES-SWA_donor_ref|MES-SWA_donor_ref_comp|MaxEntScan_alt|MaxEntScan_diff|MaxEntScan_ref|GERP++_NR|GERP++_RS|REVEL_rankscore|phastCons100way_vertebrate|phyloP100way_vertebrate|LoFtool|ExACpLI|CLINVAR|CLINVAR_CLNSIG|CLINVAR_CLNVID|CLINVAR_CLNREVSTAT|genomic_superdups_frac_match"

    header = [word.upper() for word in csq_header.split("|")]

    # WHEN parsed using the parse_variant method
    parsed_vep97_annotated_variant = parse_variant(
        variant=one_vep97_annotated_variant, vep_header=header, case=case_obj
    )

    # GIVEN a database without any variants
    adapter = real_populated_database
    assert adapter.variant_collection.find_one() is None

    # WHEN loading the variant into the database
    adapter.load_variant(variant_obj=parsed_vep97_annotated_variant)

    # THEN the variant is loaded with the fields correctly parsed
    variant = adapter.variant_collection.find_one()

    # Clinvar fields shoud be correctly parsed:
    first_clnsig = variant["clnsig"][0]
    assert first_clnsig

    # Clinvar accession should be a numberical value
    assert isinstance(first_clnsig["accession"], int)

    # Value field should be a string (i.e. pathogenic, benign,..)
    assert isinstance(first_clnsig["value"], str)

    # Revstat field should be also a string (i.e. criteria_provided, ..)
    assert isinstance(first_clnsig["revstat"], str)
