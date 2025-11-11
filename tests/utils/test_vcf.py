from scout.utils.vcf import validate_vcf_line


def test_validate_vcf_line():
    """Test the variants export VCF line validator."""

    # --- Valid SNV ---
    snv_line = "1\t1000\t.\tA\tT\t.\t.\tTYPE=SNV"
    assert validate_vcf_line("TYPE", snv_line)[0] is True

    # --- SNV with multiple ALT alleles ---
    snv_multi_alt = "1\t1000\t.\tA\tC,G\t.\t.\tTYPE=SNV"
    assert validate_vcf_line("TYPE", snv_multi_alt)[0] is True

    # --- SNV with missing ALT ---
    snv_missing_alt = "1\t1000\t.\tA\t.\t.\t.\tTYPE=SNV"
    assert validate_vcf_line("TYPE", snv_missing_alt)[0] is False

    # --- SNV with invalid ALT (symbolic) ---
    snv_invalid_alt = "1\t1000\t.\tA\tdel\t.\t.\tTYPE=SNV"
    assert validate_vcf_line("TYPE", snv_invalid_alt)[0] is False

    # --- Invalid REF (non-nucleotide) ---
    invalid_ref = "1\t1000\t.\tX\tT\t.\t.\tTYPE=SNV"
    assert validate_vcf_line("TYPE", invalid_ref)[0] is False

    # --- Valid SV (standard) ---
    sv_line = "2\t2000\t.\tN\t<DEL>\t.\t.\tEND=2050;SVTYPE=DEL"
    assert validate_vcf_line("SVTYPE", sv_line)[0] is True

    # --- Valid SV with extended ALT ---
    sv_extended = "3\t3000\t.\tN\t<INS:ME>\t.\t.\tEND=3050;SVTYPE=INS"
    assert validate_vcf_line("SVTYPE", sv_extended)[0] is True

    # --- Invalid SV (ALT missing angle brackets) ---
    sv_missing_brackets = "2\t2000\t.\tN\tDEL\t.\t.\tEND=2050;SVTYPE=DEL"
    assert validate_vcf_line("SVTYPE", sv_missing_brackets)[0] is False

    # --- BND / breakend ALT tests ---
    bnd1 = "4\t4000\t.\tN\tN]chr2:12345]\t.\t.\tSVTYPE=BND"
    assert validate_vcf_line("SVTYPE", bnd1)[0] is True

    bnd2 = "5\t5000\t.\tN\t[chr3:54321[N\t.\t.\tSVTYPE=BND"
    assert validate_vcf_line("SVTYPE", bnd2)[0] is True

    bnd3 = "6\t6000\t.\tN\tA]chr1:11111]\t.\t.\tSVTYPE=BND"
    assert validate_vcf_line("SVTYPE", bnd3)[0] is True

    # --- Invalid BND ALT ---
    invalid_bnd = "7\t7000\t.\tN\t<DEL>\t.\t.\tSVTYPE=BND"
    assert validate_vcf_line("SVTYPE", invalid_bnd)[0] is False

    # --- QUAL field tests ---
    snv_invalid_qual = "1\t1000\t.\tA\tT\tXYZ\t.\tTYPE=SNV"
    assert validate_vcf_line("TYPE", snv_invalid_qual)[0] is False

    sv_valid_qual = "2\t2000\t.\tN\t<DEL>\t99.5\t.\tEND=2050;SVTYPE=DEL"
    assert validate_vcf_line("SVTYPE", sv_valid_qual)[0] is True

    # --- FILTER field tests ---
    snv_invalid_filter = "1\t1000\t.\tA\tT\t.\tINVALID#FILTER\tTYPE=SNV"
    assert validate_vcf_line("TYPE", snv_invalid_filter)[0] is False

    sv_valid_filter = "2\t2000\t.\tN\t<DEL>\t.\tPASS\tEND=2050;SVTYPE=DEL"
    assert validate_vcf_line("SVTYPE", sv_valid_filter)[0] is True

    # --- INFO field tests ---
    snv_invalid_info = "1\t1000\t.\tA\tT\t.\t.\tTYPE="
    assert validate_vcf_line("TYPE", snv_invalid_info)[0] is False

    sv_missing_svtype_info = "2\t2000\t.\tN\t<DEL>\t.\t.\tEND=2050"
    assert validate_vcf_line("SVTYPE", sv_missing_svtype_info)[0] is False

    sv_invalid_info_pair = "2\t2000\t.\tN\t<DEL>\t.\t.\tEND="
    assert validate_vcf_line("SVTYPE", sv_invalid_info_pair)[0] is False
