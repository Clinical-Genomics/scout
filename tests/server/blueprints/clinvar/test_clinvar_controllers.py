from werkzeug.datastructures import ImmutableMultiDict

from scout.server.blueprints.clinvar.controllers import parse_chromosome_coordinates


def test_parse_chromosome_coordinates():
    """Test parsing chromosome coordinates and optional variant fields."""
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
        "OuterStart": "90",
        "InnerStart": "95",
        "InnerStop": "205",
        "OuterStop": "210",
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
