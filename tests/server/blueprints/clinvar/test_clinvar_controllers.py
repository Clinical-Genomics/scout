from werkzeug.datastructures import ImmutableMultiDict

from scout.server.blueprints.clinvar.controllers import parse_chromosome_coordinates


def test_parse_chromosome_coordinates():
    """Test parsing precise SNV chromosome coordinates and optional variant fields."""
    form = ImmutableMultiDict(
        {
            "assembly": "GRCh38",
            "chromosome": "1",
            "start": "100",
            "stop": "200",
            "outer_start": "90",
            "inner_start": "95",
            "inner_stop": "205",
            "outer_stop": "210",
            "length": "101",
            "category": "snv",
            "alt": "A",
        }
    )

    result = parse_chromosome_coordinates(form)

    assert result == {
        "assembly": "GRCh38",
        "chromosome": "1",
        "start": 100,
        "stop": 200,
        "variantLength": 101,
        "alternateAllele": "A",
    }


def test_parse_chromosome_coordinates_uses_breakpoints():
    """Test using breakpoints and converting mitochondrial chromosome notation."""
    form = ImmutableMultiDict(
        {
            "assembly": "GRCh37",
            "chromosome": "M",
            "breakpoint1": "1000",
            "breakpoint2": "2000",
            "category": "sv",
            "coordinate_type": "precise",
            "length": "1001",
        }
    )

    result = parse_chromosome_coordinates(form)

    assert result == {
        "assembly": "GRCh37",
        "chromosome": "MT",
        "start": 1000,
        "stop": 2000,
        "variantLength": 1001,
    }


def test_parse_chromosome_coordinates_uses_approximate_coordinates():
    """Test parsing approximate SV chromosome coordinates."""
    form = ImmutableMultiDict(
        {
            "assembly": "GRCh37",
            "chromosome": "20",
            "outer_start": "54963140",
            "inner_start": "54963189",
            "inner_stop": "54963200",
            "outer_stop": "54963300",
            "category": "sv",
            "coordinate_type": "approximate",
            "length": "61",
        }
    )

    result = parse_chromosome_coordinates(form)

    assert result == {
        "assembly": "GRCh37",
        "chromosome": "20",
        "outerStart": 54963140,
        "innerStart": 54963189,
        "innerStop": 54963200,
        "outerStop": 54963300,
        "variantLength": 61,
    }
