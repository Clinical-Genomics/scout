from scout.build import build_institute

def test_build_institute(parsed_institute):
    institute_obj = build_institute(
        internal_id = parsed_institute['institute_id'],
        display_name = parsed_institute['display_name'],
        sanger_recipients = parsed_institute['sanger_recipients'],
    )
    
    assert institute_obj.internal_id == parsed_institute['institute_id']

