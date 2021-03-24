def parse_frequencies(variant, transcripts):
    """Add the frequencies to a variant

    Frequencies are parsed either directly from keys in info fields or from the
    transcripts is they are annotated there.

    Args:
        variant(cyvcf2.Variant): A parsed vcf variant
        transcripts(iterable(dict)): Parsed transcripts

    Returns:
        frequencies(dict): A dictionary with the relevant frequencies
    """
    frequencies = {}
    # These lists could be extended...
    thousand_genomes_keys = ["1000GAF"]
    thousand_genomes_max_keys = ["1000G_MAX_AF"]

    exac_keys = ["EXACAF"]
    exac_max_keys = ["ExAC_MAX_AF", "EXAC_MAX_AF"]

    # Gnomad have both snv and sv frequencies
    gnomad_keys = ["GNOMADAF", "GNOMAD_AF", "gnomad_svAF"]
    gnomad_max_keys = ["GNOMADAF_popmax", "GNOMADAF_POPMAX", "GNOMADAF_MAX"]
    gnomad_mt_keys = ["GNOMAD_MT_AF_HOM", "GNOMAD_MT_AF_HET"]

    for test_key in thousand_genomes_keys:
        thousand_g = parse_frequency(variant, test_key)
        if thousand_g is not None:
            frequencies["thousand_g"] = thousand_g
            break

    for test_key in thousand_genomes_max_keys:
        thousand_g_max = parse_frequency(variant, test_key)
        if thousand_g_max is not None:
            frequencies["thousand_g_max"] = thousand_g_max
            break

    for test_key in exac_keys:
        exac = parse_frequency(variant, test_key)
        if exac is not None:
            frequencies["exac"] = exac
            break

    for test_key in exac_max_keys:
        exac_max = parse_frequency(variant, test_key)
        if exac_max is not None:
            frequencies["exac_max"] = exac_max
            break

    for test_key in gnomad_keys:
        gnomad = parse_frequency(variant, test_key)
        if gnomad is not None:
            frequencies["gnomad"] = gnomad
            break

    for test_key in gnomad_max_keys:
        gnomad_max = parse_frequency(variant, test_key)
        if gnomad_max is not None:
            frequencies["gnomad_max"] = gnomad_max
            break

    # For mitochondrial variants, keep both "hom" and "het" freqs
    gnomad_mt_hom = parse_frequency(variant, "GNOMAD_MT_AF_HOM")
    if gnomad_mt_hom is not None:
        frequencies["gnomad_mt_homoplasmic"] = gnomad_mt_hom

    gnomad_mt_het = parse_frequency(variant, "GNOMAD_MT_AF_HET")
    if gnomad_mt_het is not None:
        frequencies["gnomad_mt_heteroplasmic"] = gnomad_mt_het

    # Search transcripts if not found in VCF
    if not frequencies:
        for transcript in transcripts:
            exac = transcript.get("exac_maf")
            exac_max = transcript.get("exac_max")

            thousand_g = transcript.get("thousand_g_maf")
            thousandg_max = transcript.get("thousandg_max")

            gnomad = transcript.get("gnomad_maf")
            gnomad_max = transcript.get("gnomad_max")

            gnomad_mt_hom = transcript.get("gnomad_mt_homoplasmic")
            gnomad_mt_het = transcript.get("gnomad_mt_heteroplasmic")

            if exac:
                frequencies["exac"] = exac
            if exac_max:
                frequencies["exac_max"] = exac_max
            if thousand_g:
                frequencies["thousand_g"] = thousand_g
            if thousandg_max:
                frequencies["thousand_g_max"] = thousandg_max
            if gnomad:
                frequencies["gnomad"] = gnomad
            if gnomad_max:
                frequencies["gnomad_max"] = gnomad_max
            if gnomad_mt_hom:
                frequencies["gnomad_mt_homoplasmic"] = gnomad_mt_hom
            if gnomad_mt_het:
                frequencies["gnomad_mt_heteroplasmic"] = gnomad_mt_het

    # These are SV-specific frequencies
    thousand_g_left = parse_frequency(variant, "left_1000GAF")
    if thousand_g_left is not None:
        frequencies["thousand_g_left"] = thousand_g_left

    thousand_g_right = parse_frequency(variant, "right_1000GAF")
    if thousand_g_right is not None:
        frequencies["thousand_g_right"] = thousand_g_right

    return frequencies


def parse_frequency(variant, info_key):
    """Parse any frequency from the info dict

    Args:
        variant(cyvcf2.Variant)
        info_key(str)

    Returns:
        frequency(float): or None if frequency does not exist
    """
    raw_annotation = variant.INFO.get(info_key)
    raw_annotation = None if raw_annotation == "." else raw_annotation
    frequency = float(raw_annotation) if raw_annotation else None
    return frequency


def parse_sv_frequencies(variant):
    """Parsing of some custom sv frequencies

    These are very specific at the moment, this will hopefully get better over time when the
    field of structural variants are more developed.

    The more general SV frequencies like 1000G and gnomADsv are parsed in parse_frequencies.

    Args:
        variant(cyvcf2.Variant)

    Returns:
        sv_frequencies(dict)
    """
    sv_frequencies = {}

    clingen_benign_keys = [
        "clingen_cgh_benignAF",
        "clingen_cgh_benign",
        "clingen_cgh_benignOCC",
    ]

    clingen_pathogenic_keys = [
        "clingen_cgh_pathogenicAF",
        "clingen_cgh_pathogenic",
        "clingen_cgh_pathogenicOCC",
    ]

    clingen_ngi_keys = ["clingen_ngi", "clingen_ngiAF", "clingen_ngiOCC"]

    swegen_keys = ["swegen", "swegenAF"]

    decipher_keys = ["decipherAF", "decipher"]

    cg_keys = ["clinical_genomics_mipAF", "clinical_genomics_mipOCC"]

    for key in clingen_benign_keys:
        value = parse_sv_frequency(variant, key)
        if value is None:
            continue
        sv_frequencies["clingen_cgh_benign"] = value
        break

    for key in clingen_pathogenic_keys:
        value = parse_sv_frequency(variant, key)
        if value is None:
            continue
        sv_frequencies["clingen_cgh_pathogenic"] = value
        break

    for key in clingen_ngi_keys:
        value = parse_sv_frequency(variant, key)
        if value is None:
            continue
        sv_frequencies["clingen_ngi"] = value
        break

    for key in swegen_keys:
        value = parse_sv_frequency(variant, key)
        if value is None:
            continue
        sv_frequencies["swegen"] = value
        break

    for key in decipher_keys:
        value = parse_sv_frequency(variant, key)
        if value is None:
            continue
        sv_frequencies["decipher"] = value
        break

    for key in cg_keys:
        value = parse_sv_frequency(variant, key)
        if value is None:
            continue
        sv_frequencies["clingen_mip"] = value
        break

    return sv_frequencies


def parse_sv_frequency(variant, info_key):
    """Parse a SV frequency.

    These has to be treated separately since some of them are not actually frequencies(float) but
    occurances(int)
    """
    value = variant.INFO.get(info_key, 0)
    if "AF" in info_key:
        value = float(value)
    else:
        value = int(value)
    if value > 0:
        return value
    return None
