def test_rank_model_from_url_snv(adapter, case_obj):
    """Test parsing and saving a SNV rank model object from a remote config file"""

    # GIVEN that the params to retrieve a SNV genetic model are available in the app context
    RANK_MODEL_LINK_PREFIX = "https://raw.githubusercontent.com/Clinical-Genomics/reference-files/master/rare-disease/rank_model/rank_model_-v"
    RANK_MODEL_LINK_POSTFIX = "-.ini"

    # GIVEN a rank model version saved in the case document
    rank_model_version = case_obj["rank_model_version"]

    # WHEN model is retrieved from remote server
    rank_model_dict = adapter.rank_model_from_url(
        RANK_MODEL_LINK_PREFIX, rank_model_version, RANK_MODEL_LINK_POSTFIX
    )

    # THEN rank model should be retrieved
    assert isinstance(rank_model_dict, dict)

    # And should also be saved to database
    assert adapter.rank_model_collection.find_one()


def test_rank_model_from_url_sv(adapter, case_obj):
    """Test parsing and saving a SV rank model object from a remote config file"""

    # GIVEN that the params to retrieve a SV genetic model are available in the app context
    SV_RANK_MODEL_LINK_PREFIX = "https://raw.githubusercontent.com/Clinical-Genomics/reference-files/master/rare-disease/rank_model/svrank_model_-v"
    SV_RANK_MODEL_LINK_POSTFIX = "-.ini"

    # GIVEN a rank model version saved in the case document
    rank_model_version = case_obj["sv_rank_model_version"]

    # WHEN model is retrieved from remote server
    rank_model_dict = adapter.rank_model_from_url(
        SV_RANK_MODEL_LINK_PREFIX, rank_model_version, SV_RANK_MODEL_LINK_POSTFIX
    )

    # THEN rank model should be retrieved
    assert isinstance(rank_model_dict, dict)

    # And should also be saved to database
    assert adapter.rank_model_collection.find_one()
