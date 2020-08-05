"""Tests for the loqusdb extension"""

import subprocess
from subprocess import CalledProcessError
import pytest

from scout.server.extensions.loqus_extension import LoqusDB
from scout.server.extensions.loqus_extension import execute_command as execute_command


def test_set_coordinates_no_variant_type():
    """Test update coordinates when nothing to update"""
    # GIVEN a variant with some coordinates
    pos = 10
    end = 10
    length = 1
    var = {
        "_id": "1_10_A_C",
        "pos": pos,
        "end": end,
        "length": length,
    }
    # WHEN setting the coordinates
    LoqusDB.set_coordinates(var)
    # THEN assert that nothing changed
    assert var["pos"] == pos
    assert var["end"] == end
    assert var["length"] == length


def test_set_coordinates_ins():
    """Test update coordinates when hidden insertion"""
    # GIVEN a variant with some coordinates
    pos = 10
    end = 10
    length = 10
    var_type = "INS"
    var = {
        "_id": "1_10_INS",
        "pos": pos,
        "end": end,
        "length": length,
        "variant_type": var_type,
    }
    # WHEN setting the coordinates
    LoqusDB.set_coordinates(var)
    # THEN assert that end coordinate is updated
    assert var["pos"] == pos
    assert var["end"] == end + length
    assert var["length"] == length


def test_set_coordinates_unknown_ins():
    """Test update coordinates when insertion length is unknown"""
    # GIVEN a variant with some coordinates
    pos = 10
    end = 10
    length = -1
    var_type = "INS"
    var = {
        "_id": "1_10_INS",
        "pos": pos,
        "end": end,
        "length": length,
        "variant_type": var_type,
    }
    # WHEN setting the coordinates
    LoqusDB.set_coordinates(var)
    # THEN assert that end coordinate is updated
    assert var["pos"] == pos
    assert var["end"] == end
    assert var["length"] == length


def test_loqusdb_variant(mocker, loqus_extension):
    """Test to fetch a variant from loqusdb"""
    # GIVEN a return value from loqusdb
    return_value = (
        b'{"homozygote": 0, "hemizygote": 0, "observations": 1, "chrom": "1", "start": '
        b'235918688, "end": 235918693, "ref": "CAAAAG", "alt": "C", "families": ["643594"],'
        b' "total": 3}'
    )
    mocker.patch.object(subprocess, "check_output")
    subprocess.check_output.return_value = return_value
    # WHEN fetching the variant info
    var_info = loqus_extension.get_variant({"_id": "a variant"})

    # THEN assert the info was parsed correct
    assert var_info["total"] == 3


def test_loqusdb_variant_CalledProcessError(mocker, loqus_extension):
    """Test to fetch a variant from loqusdb that raises an exception"""
    # GIVEN replacing subprocess.check_output to raise CalledProcessError
    mocker.patch.object(
        subprocess, "check_output", side_effect=CalledProcessError(123, "case_count")
    )
    with pytest.raises(CalledProcessError):
        # THEN CalledProcessError is raised and thrown
        var_info = loqus_extension.get_variant({"_id": "a variant"})


def test_loqusdb_cases(mocker, loqus_extension):
    """Test the case count function in loqus extension"""
    # GIVEN a return value from loqusdb
    nr_cases = 15
    return_value = b"%d" % nr_cases
    mocker.patch.object(subprocess, "check_output")
    subprocess.check_output.return_value = return_value
    # WHEN fetching the number of cases
    res = loqus_extension.case_count()
    # THEN assert the output is parsed correct
    assert res == nr_cases


def test_loqusdb_cases_ValueError(mocker, loqus_extension):
    """Test the case count function in loqus extension"""
    # GIVEN a return value from loqusdb which is not an int
    mocker.patch(
        "scout.server.extensions.loqus_extension.execute_command", return_value="non-sense"
    )

    # THEN assert a value error is raised, but passed, and 0 is returned
    assert loqus_extension.case_count() == 0


def test_loqusdb_case_count_CalledProcessError(mocker, loqus_extension):
    """Test the case count function in loqus extension that raises an exception"""
    # GIVEN mocking subprocess to raise CalledProcessError
    mocker.patch.object(
        subprocess, "check_output", side_effect=CalledProcessError(123, "case_count")
    )
    # THEN assert exception is caught and the value 0 is returned
    assert 0 == loqus_extension.case_count()


def test_loqusdb_wrong_version(loqus_exe):
    """Test to instantiate a loqus extension whe version is to low"""
    # GIVEN a loqusdb version < 2.5
    loqus_extension = LoqusDB(loqusdb_binary=loqus_exe, version=1.0)
    # WHEN instantiating an adapter
    with pytest.raises(EnvironmentError):
        # THEN assert a syntax error is raised since version is wrong
        loqus_extension.version_check()
