import types
import pytest
from scout.export.exon import export_exons

import logging

LOG = logging.getLogger(__name__)


def test_export_exons(real_populated_database, build=37):
    adapter = real_populated_database
    result = export_exons(adapter)
    print("r")
    print(list(result))
    print("/r")
    assert isinstance(result, types.GeneratorType)
