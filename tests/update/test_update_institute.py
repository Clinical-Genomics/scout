from scout.load.institute import load_institute


def test_load_institute(adapter, parsed_institute):
    # GIVEN a empty database
    assert sum(1 for i in adapter.institutes()) == 0

    # WHEN adding a institute
    load_institute(
        adapter=adapter,
        internal_id=parsed_institute["institute_id"],
        display_name=parsed_institute["display_name"],
        sanger_recipients=parsed_institute["sanger_recipients"],
    )
    # THEN see that the institute is added to database
    institute_obj = adapter.institute(parsed_institute["institute_id"])
    assert institute_obj["internal_id"] == institute_obj["_id"] == parsed_institute["institute_id"]
