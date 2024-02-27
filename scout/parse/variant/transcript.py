from scout.parse.variant.transcript import parse_transcripts


def test_parse_cosmic_csq_cosmic():
    """Test parsing cosmic IDs from 'COSMIC' CSQ entry"""

    cosmic_id = "COSV99072206"

    # GIVEN a CSQ entry containing a specific 'COSMIC' key
    csq_header = "Consequence|COSMIC|COSMIC_CDS|COSMIC_GENE|COSMIC_STRAND|COSMIC_CNT|COSMIC_AA"
    csq_entry = "missense_variant|{0}|c.913T>G|POLQ||2|p.S305A".format(cosmic_id)

    header = [word.upper() for word in csq_header.split("|")]
    raw_transcripts = [dict(zip(header, entry.split("|"))) for entry in csq_entry.split(",")]

    # WHEN parsing the transcripts
    transcripts = parse_transcripts(raw_transcripts)

    # THEN the COSMIC annotation should be parsed correctly
    for transcript in transcripts:
        assert transcript["cosmic"] == [cosmic_id]


def test_parse_transcripts():
    ## GIVEN some transcript information and a vep header
    csq_entry = "A|missense_variant|MODERATE|ABCC2|ENSG00000023839|Transcript|ENST00000370449|protein_coding|10/32||ENST00000370449.4:c.1249G>A|ENSP00000359478.4:p.Val417Ile|1362|1249|417|V/I|Gtt/Att|||1||HGNC|53|YES|||CCDS7484.1|ENSP00000359478|Q92887||UPI000013D6CA||Ensembl|G|G||tolerated|benign|PROSITE_profiles:PS50929&hmmpanther:PTHR24223&hmmpanther:PTHR24223:SF176&TIGRFAM_domain:TIGR00957&Pfam_domain:PF00664&Gene3D:2hydA01&Superfamily_domains:SSF90123||||||12.834|9.654|8.373|10.218|-7.208|1.111|-6.097|-6.097|-12.417|-1.215|-9.514|-13.633||||5.48|-10.3|0.54096|0.000000|-0.327000|0.0978|0.00|255992|Benign|255992|criteria_provided&_multiple_submitters&_no_conflicts|,A|missense_variant|MODERATE|ABCC2|1244|Transcript|NM_000392.3|protein_coding|10/32||NM_000392.3:c.1249G>A|NP_000383.1:p.Val417Ile|1388|1249|417|V/I|Gtt/Att|||1||EntrezGene|53|YES||||NP_000383.1|||||RefSeq|G|G||tolerated|benign|||||||12.834|9.654|8.373|10.218|-7.208|1.111|-6.097|-6.097|-12.417|-1.215|-9.514|-13.633||||5.48|-10.3|0.54096|0.000000|-0.327000|0.0978|0.00|255992|Benign|255992|criteria_provided&_multiple_submitters&_no_conflicts|,A|missense_variant|MODERATE|ABCC2|1244|Transcript|NM_000392.4|protein_coding|10/32||NM_000392.4:c.1249G>A|NP_000383.1:p.Val417Ile|1496|1249|417|V/I|Gtt/Att|||1||EntrezGene|53|YES||||NP_000383.1||||rseq_mrna_nonmatch&rseq_cds_mismatch|RefSeq|G|G|OK|tolerated|benign|||||||12.834|9.654|8.373|10.218|-7.208|1.111|-6.097|-6.097|-12.417|-1.215|-9.514|-13.633||||5.48|-10.3|0.54096|0.000000|-0.327000|0.0978|0.00|255992|Benign|255992|criteria_provided&_multiple_submitters&_no_conflicts|"

    csq_header = "Allele|Consequence|IMPACT|SYMBOL|Gene|Feature_type|Feature|BIOTYPE|EXON|INTRON|HGVSc|HGVSp|cDNA_position|CDS_position|Protein_position|Amino_acids|Codons|Existing_variation|DISTANCE|STRAND|FLAGS|SYMBOL_SOURCE|HGNC_ID|CANONICAL|TSL|APPRIS|CCDS|ENSP|SWISSPROT|TREMBL|UNIPARC|REFSEQ_MATCH|SOURCE|GIVEN_REF|USED_REF|BAM_EDIT|SIFT|PolyPhen|DOMAINS|HGVS_OFFSET|MOTIF_NAME|MOTIF_POS|HIGH_INF_POS|MOTIF_SCORE_CHANGE|MES-NCSS_downstream_acceptor|MES-NCSS_downstream_donor|MES-NCSS_upstream_acceptor|MES-NCSS_upstream_donor|MES-SWA_acceptor_alt|MES-SWA_acceptor_diff|MES-SWA_acceptor_ref|MES-SWA_acceptor_ref_comp|MES-SWA_donor_alt|MES-SWA_donor_diff|MES-SWA_donor_ref|MES-SWA_donor_ref_comp|MaxEntScan_alt|MaxEntScan_diff|MaxEntScan_ref|GERP++_NR|GERP++_RS|REVEL_rankscore|phastCons100way_vertebrate|phyloP100way_vertebrate|LoFtool|ExACpLI|CLINVAR|CLINVAR_CLNSIG|CLINVAR_CLNVID|CLINVAR_CLNREVSTAT|genomic_superdups_frac_match"

    header = [word.upper() for word in csq_header.split("|")]

    raw_transcripts = [dict(zip(header, entry.split("|"))) for entry in csq_entry.split(",")]
    assert len(raw_transcripts) == 3

    ## WHEN parsing the transcript
    transcripts = parse_transcripts(raw_transcripts)
    for transcript in transcripts:
        ## THEN assert that some information was correct
        if transcript["transcript_id"] == "ENST00000370449":
            assert transcript["sift_prediction"] == "tolerated"
            assert transcript["functional_annotations"] == ["missense_variant"]
            assert transcript["gerp"] == "-10.3"
            assert transcript["phast"] == "0.000000"
            assert transcript["phylop"] == "-0.327000"
            assert transcript["revel_rankscore"] == 0.54096


def test_parse_functional_annotation(vep_csq_header, vep_csq):
    """Test parsing functional annotation"""
    ## GIVEN a transcript with the functional annotation in the CSQ
    header = [word.upper() for word in vep_csq_header.split("|")]
    raw_transcripts = [dict(zip(header, entry.split("|"))) for entry in vep_csq.split(",")]
    transcripts = parse_transcripts(raw_transcripts)

    for transcript in transcripts:
        assert transcript["functional_annotations"] == ["synonymous_variant"]


def test_parse_optional_hgnc_annotation(vep_csq_header, vep_csq):
    """Test parsing the HGNC id from the CSQ field"""
    ## GIVEN a transcript with the optional hgnc annotation
    header = [word.upper() for word in vep_csq_header.split("|")]
    raw_transcripts = [dict(zip(header, entry.split("|"))) for entry in vep_csq.split(",")]
    ## WHEN parsing the transcripts
    transcripts = parse_transcripts(raw_transcripts)

    ## THEN assert that the hgnc annotation is parsed correctly
    for transcript in transcripts:
        assert transcript["functional_annotations"] == ["synonymous_variant"]
        assert transcript["hgnc_id"] == 10593


def test_parse_vep_freq_thousand_g():
    ## GIVEN a transcript with the 1000G frequency
    freq = 0.01
    csq_header = "Allele|Consequence|1000GAF"
    csq_entry = "C|missense_variant|{0}".format(freq)

    header = [word.upper() for word in csq_header.split("|")]

    raw_transcripts = [dict(zip(header, entry.split("|"))) for entry in csq_entry.split(",")]

    ## WHEN parsing the transcripts
    transcripts = parse_transcripts(raw_transcripts)

    ## THEN assert that the 1000GAF annotation is parsed correctly
    for transcript in transcripts:
        assert transcript["thousand_g_maf"] == freq


def test_parse_vep_freq_thousand_g_alt(vep_csq_header, vep_csq):
    """Test extracting the 1000G allele frequency (AF) from the CSQ entry"""
    ## GIVEN a transcript with the 1000G frequency
    freq = 0.9242
    header = [word.upper() for word in vep_csq_header.split("|")]

    raw_transcripts = [dict(zip(header, entry.split("|"))) for entry in vep_csq.split(",")]

    ## WHEN parsing the transcripts
    transcripts = parse_transcripts(raw_transcripts)

    ## THEN assert that the AF annotation is parsed correctly
    for transcript in transcripts:
        assert transcript["thousand_g_maf"] == freq


def test_parse_vep_freq_gnomad(vep_csq_header, vep_csq):
    """Test extracting the gnomAD AF (gnomAD_AF) from the CSQ field"""
    ## GIVEN a transcript with the gnomAD_AF key/value

    header = [word.upper() for word in vep_csq_header.split("|")]
    raw_transcripts = [dict(zip(header, entry.split("|"))) for entry in vep_csq.split(",")]

    gnomad_maf = float(raw_transcripts[0]["GNOMAD_AF"])

    ## WHEN parsing the transcripts
    transcripts = parse_transcripts(raw_transcripts)

    ## THEN assert that the gnomAD_AF annotation is parsed correctly
    for transcript in transcripts:
        assert transcript["gnomad_maf"] == gnomad_maf
        assert transcript["gnomad_max"]


def test_parse_vep_freq_mtgnomad(vep_csq_header, vep_csq):
    """Test extracting the mitochondrial gnomAD AF (gnomAD_mt_AF_hom/het) from the CSQ field"""
    ## GIVEN a transcript with the gnomAD_AF key/value

    header = [word.upper() for word in vep_csq_header.split("|")]
    raw_transcripts = [dict(zip(header, entry.split("|"))) for entry in vep_csq.split(",")]

    gnomad_mt_hom = float(raw_transcripts[0]["GNOMAD_MT_AF_HOM"])
    gnomad_mt_het = float(raw_transcripts[0]["GNOMAD_MT_AF_HET"])

    ## WHEN parsing the transcripts
    transcripts = parse_transcripts(raw_transcripts)

    ## THEN assert that the gnomAD_AF annotation is parsed correctly
    for transcript in transcripts:
        assert transcript["gnomad_mt_homoplasmic"] == gnomad_mt_hom
        assert transcript["gnomad_mt_heteroplasmic"] == gnomad_mt_het


def test_parse_vep_freq_exac():
    """Test extracting the EXAC MAX AF from the CSQ field"""
    ## GIVEN a transcript with the 1000G frequency
    freq = 0.01
    csq_header = "Allele|Consequence|EXAC_MAX_AF"
    csq_entry = "C|missense_variant|{0}".format(freq)
    header = [word.upper() for word in csq_header.split("|")]

    raw_transcripts = [dict(zip(header, entry.split("|"))) for entry in csq_entry.split(",")]

    ## WHEN parsing the transcripts
    transcripts = parse_transcripts(raw_transcripts)

    ## THEN assert that the hgnc annotation is parsed correct
    for transcript in transcripts:
        assert transcript["exac_max"] == freq


def test_parse_vep_freq_thousand_g_max():
    """Test parsing thousandg_max value from the CSQ field"""

    ## GIVEN a transcript with the 1000G AFR_AF and AMR_AF frequencies
    freqs = [0.01, 0.001]
    csq_header = "Allele|Consequence|AFR_AF|AMR_AF"
    csq_entry = "C|missense_variant|{0}|{1}".format(freqs[0], freqs[1])
    header = [word.upper() for word in csq_header.split("|")]

    raw_transcripts = [dict(zip(header, entry.split("|"))) for entry in csq_entry.split(",")]

    ## WHEN parsing the transcripts
    transcripts = parse_transcripts(raw_transcripts)

    ## THEN assert that the hgnc annotation is parsed correct
    for transcript in transcripts:
        assert transcript["thousandg_max"] == max(freqs)


def test_parse_superdups_fractmatch():
    """Test extracting genomic_superdups_frac_match values from the CSQ field"""

    # GIVEN a transcript with the UCSC superdups fracMatch
    fract_match = [0.992904, 0.98967]
    csq_header = "Allele|Consequence|genomic_superdups_frac_match"
    csq_entry = "C|missense_variant|{0}&{1}".format(fract_match[0], fract_match[1])

    header = [word.upper() for word in csq_header.split("|")]
    raw_transcripts = [dict(zip(header, entry.split("|"))) for entry in csq_entry.split(",")]

    assert raw_transcripts[0]["GENOMIC_SUPERDUPS_FRAC_MATCH"] == "0.992904&0.98967"

    ## WHEN parsing the transcripts
    transcripts = parse_transcripts(raw_transcripts)
    for transcript in transcripts:
        assert transcript["superdups_fracmatch"] == fract_match


def test_parse_cadd(vep_csq_header, vep_csq):
    """Testing parsing of CADD_PHRED score from VEP-annotated transcripts"""

    # GIVEN a transcript with the CADD score in th CSQ
    header = [word.upper() for word in vep_csq_header.split("|")]
    raw_transcripts = [dict(zip(header, entry.split("|"))) for entry in vep_csq.split(",")]

    tx_cadd = float(raw_transcripts[0].get("CADD_PHRED"))

    ## WHEN parsing the transcripts
    transcripts = list(parse_transcripts(raw_transcripts))

    # CADD score should be parsed correctly
    assert isinstance(transcripts[0]["cadd"], float)
    assert transcripts[0]["cadd"] == tx_cadd


def test_parse_spliceai(vep_103_csq_header, vep_103_csq):
    """Testing parsing of CADD_PHRED score from VEP-annotated transcripts"""

    # GIVEN a transcript with the CADD score in th CSQ
    header = [word.upper() for word in vep_103_csq_header.split("|")]
    raw_transcripts = [dict(zip(header, entry.split("|"))) for entry in vep_103_csq.split(",")]

    tx_spliceai_delta_position = 3

    ## WHEN parsing the transcripts
    transcripts = list(parse_transcripts(raw_transcripts))

    # CADD score should be parsed correctly
    assert isinstance(transcripts[0]["spliceai_delta_score"], float)
    assert transcripts[0]["spliceai_delta_position"] == tx_spliceai_delta_position


def test_parse_hg38_mane_transcripts(vep_csq_header, vep_csq):
    """Testing MANE trascripts parsing for genome build 38"""
    # GIVEN a transcript with the MANE trancript value in th CSQ
    header = [word.upper() for word in vep_csq_header.split("|")]
    raw_transcripts = [dict(zip(header, entry.split("|"))) for entry in vep_csq.split(",")]

    ## WHEN parsing the transcripts
    transcripts = parse_transcripts(raw_transcripts)

    ## THEN assert that the MANE annotation is parsed correctly
    for transcript in transcripts:
        assert transcript["mane_select_transcript"] == "NM_000335.5"
        assert transcript["mane_plus_clinical_transcript"] == "NM_001099404.2"
