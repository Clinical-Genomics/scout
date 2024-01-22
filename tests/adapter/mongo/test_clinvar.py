def test_clinvar_variant_submitter(adapter, institute_obj, case_obj, variant_obj, user_obj):
    """Test the function that returns the name of the user which added a specific variant to a submission."""

    # GIVEN an event created when a variant has been added to a ClinVar submission
    link = f"/{institute_obj['_id']}/{case_obj['display_name']}/{variant_obj['_id']}"
    adapter.create_event(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        category="variant",
        verb="clinvar_add",
        variant=variant_obj,
        subject=variant_obj["display_name"],
    )
    assert adapter.event_collection.find_one({"verb": "clinvar_add"})

    # Then the clinvar_variant_submitter should return the name of the user which added the variant to the submission in the first place
    assert (
        adapter.clinvar_variant_submitter(
            institute_id=institute_obj["_id"],
            case_id=case_obj["_id"],
            variant_id=variant_obj["_id"],
        )
        == user_obj["name"]
    )
