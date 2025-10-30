from scout.utils.vcf import validate_vcf_line


def test_validate_vcf_line():
    """Test the variants export VCF line validator."""

    # --- Valid SNV ---
    snv_line = "1\t1000\t.\tA\tT\t.\t.\tTYPE=SNV"
    assert validate_vcf_line("TYPE", snv_line) is True

    # --- SNV with multiple ALT alleles ---
    snv_multi_alt = "1\t1000\t.\tA\tC,G\t.\t.\tTYPE=SNV"
    assert validate_vcf_line("TYPE", snv_multi_alt) is True

    # --- SNV with missing ALT ---
    snv_missing_alt = "1\t1000\t.\tA\t.\t.\t.\tTYPE=SNV"
    assert validate_vcf_line("TYPE", snv_missing_alt) is False

    # --- SNV with invalid ALT (symbolic) ---
    snv_invalid_alt = "1\t1000\t.\tA\tdel\t.\t.\tTYPE=SNV"
    assert validate_vcf_line("TYPE", snv_invalid_alt) is False

    # --- Invalid REF (non-nucleotide) ---
    invalid_ref = "1\t1000\t.\tX\tT\t.\t.\tTYPE=SNV"
    assert validate_vcf_line("TYPE", invalid_ref) is False

    # --- Valid SV (standard) ---
    sv_line = "2\t2000\t.\tN\t<DEL>\t.\t.\tEND=2050;SVTYPE=DEL"
    assert validate_vcf_line("SVTYPE", sv_line) is True

    # --- Valid SV with extended ALT ---
    sv_extended = "3\t3000\t.\tN\t<INS:ME>\t.\t.\tEND=3050;SVTYPE=INS"
    assert validate_vcf_line("SVTYPE", sv_extended) is True

    # --- Invalid SV (ALT is nucleotide) ---
    sv_invalid_alt = "2\t2000\t.\tN\tA\t.\t.\tEND=2050;SVTYPE=DEL"
    assert validate_vcf_line("SVTYPE", sv_invalid_alt) is False

    # --- Invalid SV (ALT missing angle brackets) ---
    sv_missing_brackets = "2\t2000\t.\tN\tDEL\t.\t.\tEND=2050;SVTYPE=DEL"
    assert validate_vcf_line("SVTYPE", sv_missing_brackets) is False

    # --- QUAL field tests ---
    snv_invalid_qual = "1\t1000\t.\tA\tT\tXYZ\t.\tTYPE=SNV"
    assert validate_vcf_line("TYPE", snv_invalid_qual) is False

    sv_valid_qual = "2\t2000\t.\tN\t<DEL>\t99.5\t.\tEND=2050;SVTYPE=DEL"
    assert validate_vcf_line("SVTYPE", sv_valid_qual) is True

    # --- FILTER field tests ---
    snv_invalid_filter = "1\t1000\t.\tA\tT\t.\tINVALID#FILTER\tTYPE=SNV"
    assert validate_vcf_line("TYPE", snv_invalid_filter) is False

    sv_valid_filter = "2\t2000\t.\tN\t<DEL>\t.\tPASS\tEND=2050;SVTYPE=DEL"
    assert validate_vcf_line("SVTYPE", sv_valid_filter) is True

    # --- INFO field tests ---
    snv_invalid_info = "1\t1000\t.\tA\tT\t.\t.\tTYPE="
    assert validate_vcf_line("TYPE", snv_invalid_info) is False

    sv_missing_svtype_info = "2\t2000\t.\tN\t<DEL>\t.\t.\tEND=2050"
    assert validate_vcf_line("SVTYPE", sv_missing_svtype_info) is False

    sv_invalid_info_pair = "2\t2000\t.\tN\t<DEL>\t.\t.\tEND="
    assert validate_vcf_line("SVTYPE", sv_invalid_info_pair) is False
