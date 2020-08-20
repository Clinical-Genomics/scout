import pytest
from scout.export.gene import export_genes
import types


# TODO: Not a good test, there are no exons in the database!
def test_export_genes(real_populated_database):
    adapter = real_populated_database
    result = export_genes(adapter)
    assert isinstance(result, types.GeneratorType)
