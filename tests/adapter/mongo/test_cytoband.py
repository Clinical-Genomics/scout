# -*- coding: utf-8 -*-


def test_cytoband_by_chrom(real_populated_database):
    """Test function that returns cytobands by chromosome dictionary"""

    test_cytobands = [
        {
            "_id": "7d3c64026fd1a3ae032f9715a82eac46",
            "band": "p36.31",
            "chrom": "1",
            "start": "5400000",
            "stop": "7200000",
            "build": "37",
        },
        {
            "_id": "b68883bc2b2b30af28d4e1958c6c9bb8",
            "band": "p36.33",
            "chrom": "1",
            "start": "0",
            "stop": "2300000",
            "build": "37",
        },
        {
            "_id": "0fb17721ec1e60adae5775883c965ca6",
            "band": "p24.2",
            "chrom": "3",
            "start": "23900000",
            "stop": "26400000",
            "build": "37",
        },
        {
            "_id": "56d086cf19ed191dd8be20c22412d217",
            "band": "p36.32",
            "chrom": "1",
            "start": "2300000",
            "stop": "5400000",
            "build": "37",
        },
    ]

    # Having a database collection containing cytobands:
    adapter = real_populated_database
    adapter.cytoband_collection.insert_many(test_cytobands)

    # The cytobands by chromosome function should return the expected result
    result = adapter.cytoband_by_chrom("37")
    assert len(result["1"]["cytobands"]) == 3
    assert len(result["3"]["cytobands"]) == 1
