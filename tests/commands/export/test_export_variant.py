from scout.utils.vcf import validate_vcf_line


def test_validate_vcf_line():
    """Test the variants export VCF line validator."""

    # --- Valid SNV ---
    snv_line = "1\t1000\t.\tA\tT\t.\t.\tTYPE=SNV"
    assert validate_vcf_line("TYPE", snv_line) is True

    # --- SNV with missing ALT ---
    snv_missing_alt = "1\t1000\t.\tA\t.\t.\t.\tTYPE=SNV"
    assert validate_vcf_line("TYPE", snv_missing_alt) is False

    # --- Invalid SNV (ALT has symbolic) ---
    snv_invalid_alt = "1\t1000\t.\tA\tdel\t.\t.\tTYPE=SNV"
    assert validate_vcf_line("TYPE", snv_invalid_alt) is False

    # --- Valid SV ---
    sv_line = "2\t2000\t.\tN\t<DEL>\t.\t.\tEND=2050;SVTYPE=DEL"
    assert validate_vcf_line("SVTYPE", sv_line) is True

    # --- Invalid SV (ALT is nucleotide) ---
    sv_invalid_alt = "2\t2000\t.\tN\tA\t.\t.\tEND=2050;SVTYPE=DEL"
    assert validate_vcf_line("SVTYPE", sv_invalid_alt) is False

    # --- Invalid REF (non-nucleotide) ---
    invalid_ref = "1\t1000\t.\tX\tT\t.\t.\tTYPE=SNV"
    assert validate_vcf_line("TYPE", invalid_ref) is False
