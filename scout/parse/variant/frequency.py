from typing import Dict

import cyvcf2

swegen_keys = ["swegen", "swegenAF", "SWEGENAF"]


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

    update_frequency_from_vcf(frequencies, variant, exac_keys, "exac")
    update_frequency_from_vcf(frequencies, variant, exac_max_keys, "exac_max")
    update_frequency_from_vcf(frequencies, variant, gnomad_keys, "gnomad")
    update_frequency_from_vcf(frequencies, variant, swegen_keys, "swegen")
    update_frequency_from_vcf(frequencies, variant, gnomad_max_keys, "gnomad_max")
    update_frequency_from_vcf(frequencies, variant, thousand_genomes_keys, "thousand_g")
    update_frequency_from_vcf(frequencies, variant, thousand_genomes_max_keys, "thousand_g_max")

    # For mitochondrial variants, keep both "hom" and "het" freqs
    update_frequency_from_vcf(frequencies, variant, ["GNOMAD_MT_AF_HOM"], "gnomad_mt_homoplasmic")
    update_frequency_from_vcf(frequencies, variant, ["GNOMAD_MT_AF_HET"], "gnomad_mt_heteroplasmic")

    # Search transcripts if not found in VCF
    if not frequencies:
        update_frequency_from_transcript(frequencies, transcripts)

    # These are SV-specific frequencies
    update_frequency_from_vcf(frequencies, variant, ["left_1000GAF"], "thousand_g_left")
    update_frequency_from_vcf(frequencies, variant, ["right_1000GAF"], "thousand_g_right")

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


def parse_sv_frequencies(variant: cyvcf2.Variant) -> Dict:
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

    decipher_keys = ["decipherAF", "decipher"]
    cg_keys = ["clinical_genomics_mipAF", "clinical_genomics_mipOCC"]

    update_sv_frequency_from_vcf(sv_frequencies, variant, clingen_benign_keys, "clingen_cgh_benign")
    update_sv_frequency_from_vcf(
        sv_frequencies, variant, clingen_pathogenic_keys, "clingen_cgh_pathogenic"
    )
    update_sv_frequency_from_vcf(sv_frequencies, variant, clingen_ngi_keys, "clingen_ngi")
    update_sv_frequency_from_vcf(sv_frequencies, variant, swegen_keys, "swegen")
    update_sv_frequency_from_vcf(sv_frequencies, variant, decipher_keys, "decipher")
    update_sv_frequency_from_vcf(sv_frequencies, variant, cg_keys, "clingen_mip")

    return sv_frequencies


def parse_mei_frequencies(variant: cyvcf2.Variant) -> Dict:
    """Parsing of some custom mei frequencies."""

    swegen_alu_keys = ["swegen_alu_FRQ", "swegen_alu_OCC"]
    swegen_herv_keys = ["swegen_herv_FRQ", "swegen_herv_OCC"]
    swegen_l1_keys = ["swegen_l1_FRQ", "swegen_l1_OCC"]
    swegen_sva_keys = ["swegen_sva_FRQ", "swegen_sva_OCC"]

    mei_frequencies = {}

    update_sv_frequency_from_vcf(mei_frequencies, variant, swegen_alu_keys, "swegen_alu")
    update_sv_frequency_from_vcf(mei_frequencies, variant, swegen_herv_keys, "swegen_herv")
    update_sv_frequency_from_vcf(mei_frequencies, variant, swegen_l1_keys, "swegen_l1")
    update_sv_frequency_from_vcf(mei_frequencies, variant, swegen_sva_keys, "swegen_sva")

    if any(mei_frequencies.values()):
        max_mei_frequency = max(mei_frequencies.values())
        mei_frequencies["swegen_mei_max"] = max_mei_frequency

    return mei_frequencies


def parse_sv_frequency(variant, info_key):
    """Parse a SV frequency.

    These have to be treated separately since some of them are not actually frequencies(float) but
    occurences(int)
    """
    value = variant.INFO.get(info_key, 0)
    if any([float_str in info_key.upper() for float_str in ["AF", "FRQ"]]):
        value = float(value)
    else:
        value = int(value)
    if value > 0:
        return value
    return None


def update_frequency_from_vcf(frequency, variant, key_list, new_key):
    """Update frequency dict if key is found

    Args:
       frequency(dict)
       variant(cyvcf2.Variant)
       key_list(str list)
       new_key: (str, key for frequency)
    Returns:
       frequency(dict): Updated if key of key_list is found in variant
    """

    for the_key in key_list:
        result = parse_frequency(variant, the_key)
        if result is not None:
            frequency[new_key] = result
            break


def update_sv_frequency_from_vcf(frequency, variant, key_list, new_key):
    """Update frequency dict if key is found. Treat frequencies as float and
    occurances as int.

    Args:
       frequency(dict)
       variant(cyvcf2.Variant)
       key_list(str list)
       new_key: (str, key for frequency)
    Returns:
       frequency(dict): Updated if key of key_list is found in variant
    """

    for the_key in key_list:
        result = parse_sv_frequency(variant, the_key)
        if result is not None:
            frequency[new_key] = result
            break


def update_frequency_from_transcript(frequencies, transcripts):
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
