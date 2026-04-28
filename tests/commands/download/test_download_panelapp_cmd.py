import json

from pytest import MonkeyPatch

from scout.commands.download.panelapp import panelapp_all
from scout.constants.panels import PANELAPP_OUTFILE_NAME

DEMO_PANELS = [1207, 1141, 399]


def test_download_panelapp_all(
    empty_mock_app: app.Flask, monkeypatch: MonkeyPatch, tmp_path: Any, panelapp_panel_lookup: dict
):
    """Test the CLI that downloads all gene panels from PanelApp."""

    runner = empty_mock_app.test_cli_runner()

    # GIVEN a patched response PanelApp extension
    def fake_get_panel_ids(self, *args, **kwargs):
        return DEMO_PANELS

    monkeypatch.setattr(
        "scout.server.extensions.panelapp_extension.PanelAppClient.get_panel_ids",
        fake_get_panel_ids,
    )

    def fake_get_panel(self, panel_id: int):
        return panelapp_panel_lookup(panel_id)

    monkeypatch.setattr(
        "scout.server.extensions.panelapp_extension.PanelAppClient.get_panel",
        fake_get_panel,
    )

    # THEN when PanelApp panels are downloaded
    result = runner.invoke(panelapp_all, ["--out-dir", str(tmp_path)])
    assert result.exit_code == 0

    output_file = tmp_path / PANELAPP_OUTFILE_NAME
    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as f:
        written_panels = [json.loads(line) for line in f if line.strip()]

    # Each panel will be found in the outfile
    for panel in written_panels:
        assert panel["id"] in DEMO_PANELS
