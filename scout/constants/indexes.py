from pymongo import (IndexModel, ASCENDING, DESCENDING)

INDEXES = {
    'hgnc_collection': [IndexModel(
        [('build', ASCENDING), ('chromosome', ASCENDING)], name="build_chromosome"),
    ],
    'variant_collection': [
        IndexModel([('case_id', ASCENDING),('rank_score', DESCENDING)], name="caseid_rankscore"),
        IndexModel([('case_id', ASCENDING),('variant_rank', ASCENDING)], name="caseid_variantrank")
    ]
}
