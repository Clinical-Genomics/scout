from scout.parse.variant.frequency import parse_frequencies, parse_frequency, parse_sv_frequencies


def test_parse_frequency(cyvcf2_variant):
    # GIVEN a variant dict with a frequency in info_dict
    variant = cyvcf2_variant

    variant.INFO["1000G"] = 0.01

    # WHEN frequency is parsed
    frequency = parse_frequency(variant, "1000G")

    # THEN the frequency should be a float with correct value

    assert frequency == float(variant.INFO["1000G"])


def test_parse_frequency_non_existing_keyword(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN a variant dict with a frequency in info_dict
    variant.INFO["1000G"] = 0.01

    # WHEN frequency is parsed with wrong keyword
    frequency = parse_frequency(variant, "EXACAF")

    # THEN the frequency should be None
    assert frequency is None


def test_parse_frequency_non_existing_freq(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN a variant dict with a frequency in info_dict without value
    variant.INFO["1000G"] = None

    # WHEN frequency is parsed
    frequency = parse_frequency(variant, "1000G")

    # THEN the frequency should be None
    assert frequency is None


def test_parse_frequencies(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN a variant dict with a differenct frequencies
    variant.INFO["1000GAF"] = "0.01"
    variant.INFO["EXACAF"] = "0.001"
    variant.INFO["SWEGENAF"] = "0.02"

    # WHEN frequencies are parsed
    frequencies = parse_frequencies(variant, [])

    # THEN the frequencies should be returned in a dictionary
    assert frequencies["thousand_g"] == float(variant.INFO["1000GAF"])
    assert frequencies["exac"] == float(variant.INFO["EXACAF"])
    assert frequencies["swegen"] == float(variant.INFO["SWEGENAF"])


def test_parse_sv_frequencies_clingen_benign(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN a variant dict with a differenct frequencies
    variant.INFO["clingen_cgh_benignAF"] = "0.01"
    variant.INFO["clingen_cgh_benign"] = "3"

    # WHEN frequencies are parsed
    frequencies = parse_sv_frequencies(variant)

    # THEN assert that the first frequency is returned
    assert frequencies["clingen_cgh_benign"] == float(variant.INFO["clingen_cgh_benignAF"])


def test_parse_sv_frequencies_clingen_pathogenic(cyvcf2_variant):
    variant = cyvcf2_variant

    variant.INFO["clingen_cgh_pathogenicAF"] = "0.01"
    variant.INFO["clingen_cgh_pathogenic"] = "3"
    variant.INFO["clingen_cgh_pathogenicOCC"] = "0.1"

    # WHEN frequencies are parsed
    frequencies = parse_sv_frequencies(variant)

    # THEN assert that the first frequency is returned
    assert frequencies["clingen_cgh_pathogenic"] == float(variant.INFO["clingen_cgh_pathogenicAF"])


def test_parse_sv_frequencies_clingen(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN a variant dict with a differenct frequencies
    variant.INFO["clinical_genomics_mipAF"] = "0.01"
    variant.INFO["clinical_genomics_mipOCC"] = "0.02"

    # WHEN frequencies are parsed
    frequencies = parse_sv_frequencies(variant)

    # THEN assert that the first frequency is returned
    assert frequencies["clingen_mip"] == float(variant.INFO["clinical_genomics_mipAF"])


def test_parse_gnomad(one_vep97_annotated_variant):
    variant = one_vep97_annotated_variant

    # WHEN frequencies are parsed
    frequencies = parse_frequencies(variant, [])

    # THEN assert that the right frequency is returned
    assert frequencies["gnomad"] == float(variant.INFO["GNOMADAF"])


def test_parse_gnomad_0_freq(one_vep97_annotated_variant):
    variant = one_vep97_annotated_variant

    # GIVEN a variant with a gnomad frequency set to 0
    variant.INFO["GNOMADAF"] = "0.000"

    # WHEN frequencies are parsed
    frequencies = parse_frequencies(variant, [])

    # THEN assert that the right frequency is returned
    assert frequencies["gnomad"] == float(variant.INFO["GNOMADAF"])


def test_parse_sv_gnomad(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN a variant dict with a differenct frequencies
    variant.INFO["gnomad_svAF"] = "0.01"

    # WHEN frequencies are parsed
    frequencies = parse_frequencies(variant, [])

    # THEN the frequencies should be returned in a dictionary
    assert frequencies["gnomad"] == float(variant.INFO["gnomad_svAF"])


def test_parse_gnomad_popmax(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN a variant dict with a certain popmax allele frequency
    variant.INFO["GNOMADAF_popmax"] = "0.05"

    # WHEN frequencies are parsed
    frequencies = parse_frequencies(variant, [])

    # THEN assert that the last frequency is returned
    assert frequencies["gnomad_max"] == float(variant.INFO["GNOMADAF_popmax"])


def test_parse_sv_frequencies_ngi(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN a variant dict with a differenct frequencies
    variant.INFO["clingen_ngiAF"] = "0.1"
    variant.INFO["clingen_ngiOCC"] = "0.5"
    variant.INFO["clingen_ngi"] = "1"

    # WHEN frequencies are parsed
    frequencies = parse_sv_frequencies(variant)

    # THEN assert that the last frequency is returned
    assert frequencies["clingen_ngi"] == float(variant.INFO["clingen_ngi"])
