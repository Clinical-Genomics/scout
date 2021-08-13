"""Tests for execute commands function"""
import os
import subprocess

import pytest

from scout.server.extensions import loqusdb
from scout.server.extensions.loqus_extension import execute_command


def test_execute_command():
    """Test run echo with execute command"""
    # GIVEN a command to run in the shell
    output = "hello world"
    cmd = ["echo", output]
    # WHEN running it with execute command
    res = execute_command(cmd)
    # THEN assert the output is correct
    assert res.strip() == output


def test_execute_command_error(loqus_exe_app, monkeypatch):
    """Test triggering an error while executing a command in the LoqusDB module"""

    # GIVEN a mocked subprocess that gives error
    def mocksubprocess(*args, **kwargs):
        raise subprocess.CalledProcessError(None, None)

    monkeypatch.setattr(subprocess, "check_output", mocksubprocess)

    with loqus_exe_app.app_context():
        # THEN Executing a command will catch the exception and return an empty dict
        assert {} == loqusdb.get_variant({"_id": "a variant"})
