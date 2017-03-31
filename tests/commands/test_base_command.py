import pytest

from scout.commands import cli
from click.testing import CliRunner

#Sanity check for cli
def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
