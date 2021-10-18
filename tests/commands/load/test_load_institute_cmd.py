# -*- coding: utf-8 -*-

import logging
import sys

import click
import pytest

from scout.commands import cli
from scout.exceptions import ConfigError, IntegrityError
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


def test_load_institute(empty_mock_app):
    """Testing the load institute cli command"""

    ## GIVEN an empty database and some institute information
    mock_app = empty_mock_app
    runner = mock_app.test_cli_runner()
    assert runner
    ins_id = "cust000"
    display_name = "A special name"

    assert sum(1 for i in store.institute_collection.find()) == 0

    ## WHEN loading the institute into the database
    result = runner.invoke(cli, ["load", "institute", "-i", ins_id, "-d", display_name])

    ## THEN assert command exits without errors
    assert result.exit_code == 0

    ## THEN assert logging is correct
    assert (
        "Adding institute with internal_id: {0} and display_name: {1}".format(ins_id, display_name)
        in result.output
    )

    ## THEN assert institute is added
    assert sum(1 for i in store.institute_collection.find()) == 1


def test_load_institute2(empty_mock_app):
    """Testing the load institute cli command, additional tests"""

    ## GIVEN an empty database and some institute information
    mock_app = empty_mock_app
    runner = mock_app.test_cli_runner()
    assert runner
    ins_id = "cust000"
    display_name = "A special name"
    loqusdb = "loqusDB_test"

    assert sum(1 for i in store.institute_collection.find()) == 0

    ## WHEN loading the institute into the database
    result = runner.invoke(cli, ["load", "institute", "-i", ins_id, "-l", loqusdb])

    ## THEN assert command exits without errors
    assert result.exit_code == 0

    ## THEN assert logging is correct
    assert (
        "Adding institute with internal_id: {0} and display_name: {0}".format(ins_id)
        in result.output
    )

    ## THEN assert institute is added
    assert sum(1 for i in store.institute_collection.find()) == 1


def test_load_institute_exception(empty_mock_app):
    """Testing throwing an Click.Error"""
    ## GIVEN an empty database and some institute information
    mock_app = empty_mock_app
    runner = mock_app.test_cli_runner()
    assert runner
    ins_id = "cust000"
    display_name = "A special name"

    ## WHEN loading the same institute into the database twice an error code is returned
    result_ok = runner.invoke(cli, ["load", "institute", "-i", ins_id, "-d", display_name])
    result_error = runner.invoke(cli, ["load", "institute", "-i", ins_id, "-d", display_name])
    ## THEN assert exitcode is non-zero
    assert result_error.exit_code == 1
