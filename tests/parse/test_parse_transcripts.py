from scout.parse.variant.transcript import parse_transcripts

csq_build_38_header = """Allele|Consequence|IMPACT|SYMBOL|Gene|Feature_type|Feature|BIOTYPE|EXON|INTRON|HGVSc|HGVSp|cDNA_position|CDS_position|Protein_position|Amino_acids|Codons|Existing_variation|DISTANCE|STRAND|FLAGS|VARIANT_CLASS|SYMBOL_SOURCE|HGNC_ID|CANONICAL|MANE|TSL|APPRIS|CCDS|ENSP|SWISSPROT|TREMBL|UNIPARC|REFSEQ_MATCH|SOURCE|GIVEN_REF|USED_REF|BAM_EDIT|GENE_PHENO|SIFT|PolyPhen|DOMAINS|miRNA|HGVS_OFFSET|AF|AFR_AF|AMR_AF|EAS_AF|EUR_AF|SAS_AF|AA_AF|EA_AF|gnomAD_AF|gnomAD_AFR_AF|gnomAD_AMR_AF|gnomAD_ASJ_AF|gnomAD_EAS_AF|gnomAD_FIN_AF|gnomAD_NFE_AF|gnomAD_OTH_AF|gnomAD_SAS_AF|MAX_AF|MAX_AF_POPS|CLIN_SIG|SOMATIC|PHENO|PUBMED|MOTIF_NAME|MOTIF_POS|HIGH_INF_POS|MOTIF_SCORE_CHANGE|CADD_PHRED|CADD_RAW|LoFtool|MES-NCSS_downstream_acceptor|MES-NCSS_downstream_donor|MES-NCSS_upstream_acceptor|MES-NCSS_upstream_donor|MES-SWA_acceptor_alt|MES-SWA_acceptor_diff|MES-SWA_acceptor_ref|MES-SWA_acceptor_ref_comp|MES-SWA_donor_alt|MES-SWA_donor_diff|MES-SWA_donor_ref|MES-SWA_donor_ref_comp|MaxEntScan_alt|MaxEntScan_diff|MaxEntScan_ref|gnomADe|gnomADe_AF_popmax|gnomADe_AF|gnomADe_popmax|gnomADg|gnomADg_AF_popmax|gnomADg_AF|gnomADg_popmax|phyloP100way|phastCons"""

csq_build_38_entry = """T|synonymous_variant|LOW|AGRN|ENSG00000188157|Transcript|ENST00000379370|protein_coding|1/36||ENST00000379370.7:c.45G>T|ENSP00000368678.2:p.Pro15%3D|98|45|15|P|ccG/ccT|rs115173026||1||SNV|HGNC|HGNC:329|YES|NM_198576.4|1|P1|CCDS30551.1|ENSP00000368678|O00468||UPI00001D7C8B||Ensembl|G|G||1|||PROSITE_profiles:PS51257&Low_complexity_(Seg):seg&Cleavage_site_(Signalp):SignalP-noTM|||0.2825|0.3132|0.2334|0.1667|0.3489|0.3272|||0.3428|0.3172|0.2569|0.3322|0.2351|0.4483|0.3665|0.3535|0.3367|0.4483|gnomAD_FIN|benign||1|25741868|||||12.50|1.033266|0.421|7.162|9.046|||-0.089|-2.289|-2.272|-2.378|-7.286|-0.134|-7.419|-7.419||||rs115173026|0.366464|0.342849|nfe|rs115173026|0.359315|0.327412|nfe|0.852999985218048|0.619000017642975"""


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
            assert transcript["revel"] == 0.54096


def test_parse_functional_annotation():
    """Test parsing functional annotation"""
    ## GIVEN a transcript with the functional annotation in the CSQ
    header = [word.upper() for word in csq_build_38_header.split("|")]
    raw_transcripts = [
        dict(zip(header, entry.split("|"))) for entry in csq_build_38_entry.split(",")
    ]
    transcripts = parse_transcripts(raw_transcripts)

    for transcript in transcripts:
        assert transcript["functional_annotations"] == ["synonymous_variant"]


def test_parse_optional_hgnc_annotation():
    """Test parsing the HGNC id from the CSQ field"""
    ## GIVEN a transcript with the optional hgnc annotation
    header = [word.upper() for word in csq_build_38_header.split("|")]
    raw_transcripts = [
        dict(zip(header, entry.split("|"))) for entry in csq_build_38_entry.split(",")
    ]
    ## WHEN parsing the transcripts
    transcripts = parse_transcripts(raw_transcripts)

    ## THEN assert that the hgnc annotation is parsed correctly
    for transcript in transcripts:
        assert transcript["functional_annotations"] == ["synonymous_variant"]
        assert transcript["hgnc_id"] == 329


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


def test_parse_vep_freq_thousand_g_alt():
    """Test extracting the 1000G allele frequency (AF) from the CSQ entry"""
    ## GIVEN a transcript with the 1000G frequency
    freq = 0.2825
    header = [word.upper() for word in csq_build_38_header.split("|")]

    raw_transcripts = [
        dict(zip(header, entry.split("|"))) for entry in csq_build_38_entry.split(",")
    ]

    ## WHEN parsing the transcripts
    transcripts = parse_transcripts(raw_transcripts)

    ## THEN assert that the AF annotation is parsed correctly
    for transcript in transcripts:
        assert transcript["thousand_g_maf"] == freq


def test_parse_vep_freq_gnomad():
    """Test extracting the Gnomad AF from the CSQ field"""
    ## GIVEN a transcript with the gnomAD_AF
    freq = 0.3428
    header = [word.upper() for word in csq_build_38_header.split("|")]
    raw_transcripts = [
        dict(zip(header, entry.split("|"))) for entry in csq_build_38_entry.split(",")
    ]

    ## WHEN parsing the transcripts
    transcripts = parse_transcripts(raw_transcripts)

    ## THEN assert that the gnomAD_AF annotation is parsed correctly
    for transcript in transcripts:
        assert transcript["gnomad_maf"] == freq


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


def test_parse_hg38_mane_transcripts():
    """Testing MANE trascripts parsing for genome build 38"""
    # GIVEN a transcript with the MANE trancript value in th CSQ
    header = [word.upper() for word in csq_build_38_header.split("|")]
    raw_transcripts = [
        dict(zip(header, entry.split("|"))) for entry in csq_build_38_entry.split(",")
    ]

    ## WHEN parsing the transcripts
    transcripts = parse_transcripts(raw_transcripts)

    ## THEN assert that the MANE annotation is parsed correctly
    for transcript in transcripts:
        assert transcript["mane_transcript"] == "NM_198576.4"
