import types
import pytest
from scout.export.exon import export_exons

import logging
LOG = logging.getLogger(__name__)

def test_export_exons(adapter, build=37):
    result = export_exons(adapter)
    assert isinstance(result, types.GeneratorType)

  
    
