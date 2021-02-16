"""Tests for execute commands function"""
import os
import subprocess

import pytest

from scout.server.extensions.loqus_extension import execute_command

TRAVIS = os.getenv("TRAVIS")
GITHUB = True if os.getenv("CI") else False


def test_execute_command():
    """Test run echo with execute command"""
    # GIVEN a command to run in the shell
    output = "hello world"
    cmd = ["echo", output]
    # WHEN running it with execute command
    res = execute_command(cmd)
    # THEN assert the output is correct
    assert res.strip() == output


def test_execute_command_error(loqus_exe_app):
    """Test triggering an error while executing a command in the LoqusDB module"""

    # GIVEN that LoqusDB binary file is not properly configured
    with loqus_exe_app.app_context():
        # executing a command will trigger error
        with pytest.raises(Exception):
            var_info = loqusdb.get_variant({"_id": "a variant"})
