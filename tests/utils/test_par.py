from scout.constants import PAR_COORDINATES
from scout.utils.coordinates import is_par


def test_par_coordinates():
    ## GIVEN a position that is in the first par region
    chromosome = "X"
    position = 60001
    build = "37"

    ## WHEN checking the coordinates for a variant
    res = PAR_COORDINATES[build][chromosome].at(position)

    ## THEN assert that there way a hit
    assert res

    ## GIVEN a position that is not in any par region
    chromosome = "X"
    position = 26995210
    build = "37"

    ## WHEN checking the coordinates for a variant
    res = PAR_COORDINATES[build][chromosome].at(position)

    ## THEN assert that there way a hit
    assert not res


def test_is_par():
    ## GIVEN a position that is in the first par region
    chromosome = "X"
    position = 60001
    build = "37"

    ## WHEN checking the coordinates for a variant

    ## THEN assert that there way a hit
    assert is_par(chromosome, position, build)


def test_is_par_wrong_chromosome():
    ## GIVEN a position that is in the first par region
    chromosome = "1"
    position = 60001
    build = "37"

    ## WHEN checking the coordinates for the positions

    ## THEN assert that there way a hit
    assert is_par(chromosome, position, build) is False
