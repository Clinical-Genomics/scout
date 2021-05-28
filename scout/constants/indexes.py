from pymongo import ASCENDING, DESCENDING, TEXT, IndexModel

INDEXES = {
    "hgnc_gene": [
        IndexModel(
            [("build", ASCENDING), ("chromosome", ASCENDING)],
            name="build_chromosome",
            background=True,
        ),
        IndexModel(
            [("build", ASCENDING), ("hgnc_id", ASCENDING)],
            name="build_hgncid",
            background=True,
        ),
        IndexModel(
            [("build", ASCENDING), ("aliases", ASCENDING)],
            name="build_aliases",
            background=True,
        ),
        IndexModel(
            [("build", ASCENDING), ("hgnc_symbol", ASCENDING)],
            name="build_hgnc_symbol",
        ),
    ],
    "variant": [
        IndexModel(
            [
                ("case_id", ASCENDING),
                ("category", ASCENDING),
                ("rank_score", DESCENDING),
            ],
            name="caseid_rankscore",
            background=True,
        ),
        IndexModel(
            [
                ("case_id", ASCENDING),
                ("category", ASCENDING),
                ("variant_rank", ASCENDING),
            ],
            name="caseid_variantrank",
            background=True,
        ),
        IndexModel(
            [
                ("case_id", ASCENDING),
                ("category", ASCENDING),
                ("variant_type", ASCENDING),
                ("rank_score", DESCENDING),
            ],
            name="caseid_category_varianttype_rankscore",
            background=True,
        ),
        IndexModel(
            [
                ("hgnc_symbols", ASCENDING),
                ("rank_score", DESCENDING),
                ("category", ASCENDING),
                ("variant_type", ASCENDING),
            ],
            name="hgncsymbol_rankscore_category_varianttype",
            background=True,
            partialFilterExpression={"rank_score": {"$gt": 5}, "category": "snv"},
        ),
        IndexModel(
            [
                ("case_id", ASCENDING),
                ("category", ASCENDING),
                ("variant_id", ASCENDING),
            ],
            name="caseid_variantid",
            background=True,
        ),
        IndexModel(
            [
                ("case_id", ASCENDING),
                ("category", ASCENDING),
                ("variant_type", ASCENDING),
                ("chromosome", ASCENDING),
                ("start", ASCENDING),
                ("end", ASCENDING),
            ],
            name="caseid_category_chromosome_start_end",
            background=True,
        ),
        IndexModel([("sanger_ordered", ASCENDING)], name="sanger", background=True, sparse=True),
        IndexModel(
            [("variant_id", ASCENDING), ("institute", ASCENDING)],
            name="variant_id_institute",
            background=True,
        ),
    ],
    "hpo_term": [
        IndexModel([("description", ASCENDING)], name="description"),
        IndexModel([("description", TEXT)], default_language="english", name="description_text"),
        IndexModel([("hpo_number", ASCENDING)], name="number", background=True),
    ],
    "event": [
        IndexModel([("category", ASCENDING), ("verb", ASCENDING)], name="category_verb"),
        IndexModel([("variant_id", ASCENDING)], name="variant_id"),
        IndexModel(
            [
                ("institute", ASCENDING),
                ("case", ASCENDING),
                ("category", ASCENDING),
                ("verb", ASCENDING),
            ],
            name="case_verb",
        ),
        IndexModel([("user_id", ASCENDING)], name="user_events"),
    ],
    "transcript": [
        IndexModel(
            [("build", ASCENDING), ("hgnc_id", ASCENDING), ("length", DESCENDING)],
            name="hgncid_length",
            background=True,
        )
    ],
    "exon": [
        IndexModel(
            [("build", ASCENDING), ("hgnc_id", ASCENDING)],
            name="build_hgncid",
            background=True,
        )
    ],
    "case": [
        IndexModel([("synopsis", TEXT)], default_language="english", name="synopsis_text"),
        IndexModel([("causatives", ASCENDING)], name="causatives"),
        IndexModel(
            [("collaborators", ASCENDING), ("updated_at", ASCENDING)],
            name="collaborators_updated_at",
        ),
    ],
}
