"""Tests for execute commands function"""
import os
import subprocess

import pytest

from scout.server.extensions.loqus_extension import execute_command

TRAVIS = os.getenv("TRAVIS")


def test_run_execute_command():
    """Test run echo with execute command"""
    # GIVEN a command to run in the shell
    output = "hello world"
    cmd = ["echo", output]
    # WHEN running it with execute command
    res = execute_command(cmd)
    # THEN assert the output is correct
    assert res.strip() == output


def test_run_failing_command():
    """Test run a failing command with execute command"""
    # GIVEN a command that will fail when run in the shell
    cmd = ["cd", "nonexistingdirectory"]
    exception = subprocess.CalledProcessError
    if TRAVIS:
        exception = FileNotFoundError
    # WHEN running it with execute command
    with pytest.raises(exception):
        # THEN assert that an exception is raised
        execute_command(cmd)


def test_run_command_no_output():
    """Test run a command without output"""
    # GIVEN a command that returns no output
    cmd = ["cd", "./"]
    # WHEN running it with execute command
    res = execute_command(cmd)
    # THEN assert that the empty string is returned
    assert res == ""
