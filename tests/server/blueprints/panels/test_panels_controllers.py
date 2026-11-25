import pytest
from werkzeug.datastructures import FileStorage

from scout.demo import panel_path
from scout.server.blueprints.panels.controllers import panel_decode_lines, update_panel


def test_panel_decode_lines():
    """Test extracting gene lines from uploaded file"""

    # GIVEN a file containing gene data
    with open(panel_path, "rb") as pf:
        fs = FileStorage(pf)
        # WHEN the function 'panel_decode_lines' is invoked using the file
        lines = panel_decode_lines(fs)
        # it should return a list of gene lines
        assert lines


@pytest.mark.parametrize(
    "option,existing,action",
    [("add", False, "add"), ("add", True, "edit"), ("replace", True, "add")],
)
@pytest.mark.parametrize("delimiter", [";", "\t"])
def test_update_panel_preserves_transcripts(
    adapter, testpanel_obj, gene_obj, option: str, existing: bool, action: str, delimiter: str
) -> None:
    """Preserve uploaded transcripts in pending changes and the saved panel version."""
    hgnc_id = gene_obj["hgnc_id"]
    symbol = gene_obj["hgnc_symbol"]
    testpanel_obj["genes"] = [{"hgnc_id": hgnc_id, "symbol": symbol}] if existing else []
    adapter.panel_collection.insert_one(testpanel_obj)
    adapter.hgnc_collection.insert_one(gene_obj)

    transcripts = ["NM_138295", "NM_138295.5"]
    lines = [
        delimiter.join(
            [
                "hgnc_id",
                "hgnc_symbol",
                "disease_associated_transcripts",
                "genetic_disease_models",
            ]
        ),
        delimiter.join([str(hgnc_id), symbol, ",".join(transcripts), "AR"]),
    ]

    update_panel(adapter, testpanel_obj["panel_name"], lines, option)

    pending_panel = adapter.gene_panel(testpanel_obj["panel_name"])
    pending = [item for item in pending_panel["pending"] if item["action"] == action]
    assert len(pending) == 1
    assert pending[0]["info"]["disease_associated_transcripts"] == transcripts
    assert pending[0]["info"]["inheritance_models"] == ["AR"]

    new_version = str(pending_panel["version"] + 1)
    adapter.apply_pending(pending_panel, new_version)
    saved_panel = adapter.gene_panel(testpanel_obj["panel_name"])
    assert saved_panel["version"] == float(new_version)
    assert len(saved_panel["genes"]) == 1
    assert saved_panel["genes"][0]["disease_associated_transcripts"] == transcripts
    assert saved_panel["genes"][0]["inheritance_models"] == ["AR"]
