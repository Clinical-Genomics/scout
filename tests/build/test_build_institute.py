import pytest
from scout.build import build_institute


def test_build_institute(parsed_institute):
    ins = build_institute(
        internal_id=parsed_institute["institute_id"],
        display_name=parsed_institute["display_name"],
        sanger_recipients=parsed_institute["sanger_recipients"],
    )

    assert ins["internal_id"] == ins["_id"] == parsed_institute["institute_id"]
    assert isinstance(ins["sanger_recipients"], list)


def test_build_institute_no_sanger():
    ## GIVEN a institute without sanger recipients
    institute_info = dict(internal_id="cust000", display_name="test")
    ## WHEN building the institute
    ins = build_institute(
        internal_id=institute_info["internal_id"],
        display_name=institute_info["display_name"],
    )

    assert "sanger_recipients" not in ins
