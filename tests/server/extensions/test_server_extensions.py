import copy
import itertools
import subprocess

from scout.server.extensions.loqus_extension import LoqusDB


def test_loqusdb_variant(minimal_app, mocker):
    ## GIVEN a minimal app object
    version = 2.5
    return_values = [
        b"loqusdb, version 2.5",
        (
            b'{"homozygote": 0, "hemizygote": 0, "observations": 1, "chrom": "1", "start": '
            b'235918688, "end": 235918693, "ref": "CAAAAG", "alt": "C", "families": ["643594"],'
            b' "total": 3}'
        ),
    ]
    ## WHEN mocking the version call
    mocker.patch.object(subprocess, "check_output")
    subprocess.check_output.return_value = return_values[0]
    loqus_ext = LoqusDB(loqusdb_binary="loqusdb", version=version)

    subprocess.check_output.return_value = return_values[1]

    var_info = loqus_ext.get_variant({"_id": "a variant"})

    assert var_info["total"] == 3


def test_loqusdb_cases(minimal_app, mocker):
    ## GIVEN a minimal app object
    minimal_app.config["LOQUSDB_SETTINGS"] = {}
    version = 2.5
    return_values = [b"loqusdb, version 2.5", b"15"]
    mocker.patch.object(subprocess, "check_output")
    subprocess.check_output.return_value = return_values[0]
    loqus_ext = LoqusDB()
    loqus_ext.init_app(minimal_app)

    subprocess.check_output.return_value = return_values[1]

    nr_cases = loqus_ext._case_count()

    assert nr_cases == 15


def test_loqusdb_version_no_app(mocker):
    ## GIVEN a LoqusDB extension
    version = 2.5
    ## WHEN instansiating without an app object
    loqus_ext = LoqusDB(version=version)
    ## THEN check that the version was set correct
    assert loqus_ext.version == version


def test_loqusdb_version(minimal_app, mocker):
    ## GIVEN a minimal app object
    minimal_app.config["LOQUSDB_SETTINGS"] = {}
    version = 2.5
    mocker.patch.object(subprocess, "check_output")
    subprocess.check_output.return_value = b"loqusdb, version 2.5"
    loqus_ext = LoqusDB()
    loqus_ext.init_app(minimal_app)

    assert loqus_ext.version == version
