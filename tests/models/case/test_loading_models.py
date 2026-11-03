import pytest

import scout.models.case.case_loading_models as case_loading_models
from scout.models.case.case_loading_models import REPID, TRID, Image, set_custom_images


@pytest.mark.parametrize(
    ("identifier_field", "identifier", "expected_ids"),
    [
        ("str_repid", REPID, ["AFF2", "DAB1"]),
        ("str_trid", TRID, ["HTT", "FMR1"]),
    ],
)
def test_set_custom_images_wildcard(
    identifier_field, identifier, expected_ids, monkeypatch, tmp_path
):
    """Test custom image wildcard expansion for STR repetitions and tandem repeats."""
    # GIVEN an image with a wildcard identifier
    image_dir = tmp_path / "images"
    image_dir.mkdir()

    image_paths = []
    for expected_id in expected_ids:
        image_path = image_dir / f"{expected_id}.svg"
        image_path.write_text("<svg></svg>")
        image_paths.append(str(image_path))

    image = Image(
        title=f"Image for {identifier}",
        description=f"Description for {identifier}",
        width=500,
        height=100,
        path=str(image_dir / f"{identifier}.svg"),
        str_repid=identifier if identifier_field == "str_repid" else None,
        str_trid=identifier if identifier_field == "str_trid" else None,
    )

    def mock_glob(path):
        return image_paths

    monkeypatch.setattr(case_loading_models, "glob", mock_glob)

    # WHEN custom images are resolved
    result = set_custom_images([image])

    # THEN one image should be created for each matching identifier
    assert len(result) == len(expected_ids)

    for result_image, expected_id, image_path in zip(result, expected_ids, image_paths):
        assert getattr(result_image, identifier_field) == expected_id
        assert result_image.title == f"Image for {expected_id}"
        assert result_image.description == f"Description for {expected_id}"
        assert result_image.path == image_path
        assert result_image.format is None
