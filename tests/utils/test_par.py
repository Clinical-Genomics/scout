from scout.constants import PAR_COORDINATES
from scout.utils.coordinates import check_coordinates, is_par


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


def test_check_coordinates():
    ## GIVEN a regions of interest
    coordinates = {"chrom": "1", "start": 1, "end": 1000}
    chrom = "1"

    ## THEN a positin within bounds will be True
    within_bounds = 100
    assert check_coordinates(chrom, within_bounds, coordinates)
    ## THEN a positin out of bounds will be False
    out_of_bounds = 1111
    assert not check_coordinates(chrom, out_of_bounds, coordinates)
    ## THEN a positin within bounds will be True but wrong chromosome
    wrong_chrom = "2"
    assert not check_coordinates(wrong_chrom, within_bounds, coordinates)
