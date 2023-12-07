from scout.demo.resources import (
    orphadata_en_product6_reduced_path,
)
from scout.parse.orpha import get_orpha_diseases_product6
from scout.utils.handle import get_file_handle


def test_get_orpha_diseases_product6():
    # GIVEN lines from a read file
    lines = get_file_handle(orphadata_en_product6_reduced_path)

    # WHEN parsing the tree
    result = get_orpha_diseases_product6(lines=lines)
    disease = result["ORPHA:585"]

    # THEN assert disease with correct contents was returned
    assert len(result) == 4
    assert disease["description"] == "Multiple sulfatase deficiency"
    assert disease["orpha_code"] == 585
    assert disease["hgnc_ids"] == {"20376"}
