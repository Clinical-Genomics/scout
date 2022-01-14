from werkzeug.datastructures import FileStorage

from scout.demo import panel_path
from scout.server.blueprints.panels.controllers import panel_decode_lines


def test_panel_decode_lines():
    """Test extracting gene lines from uploaded file"""

    # GIVEN a file containing gene data
    with open(panel_path, "rb") as pf:
        fs = FileStorage(pf)
        # WHEN the function 'panel_decode_lines' is invoked using the file
        lines = panel_decode_lines(fs)
        # it should return a list of gene lines
        assert lines
