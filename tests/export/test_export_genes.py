import pytest
from scout.export.gene import export_genes
import types

import logging

LOG = logging.getLogger(__name__)


def test_export_exons(real_populated_database):
    adapter = real_populated_database
    result = export_genes(adapter)
    print("r")
    print(list(result))
    print("/r")
    assert isinstance(result, types.GeneratorType)
