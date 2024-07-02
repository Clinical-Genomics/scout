from pymongo import ASCENDING, DESCENDING, TEXT, IndexModel
from pymongo.collation import Collation

INDEXES = {
    "disease_term": [
        IndexModel(
            [("genes", ASCENDING)],
            name="genes",
        )
    ],
    "hgnc_gene": [
        IndexModel(
            [("build", ASCENDING), ("chromosome", ASCENDING)],
            name="build_chromosome",
        ),
        IndexModel(
            [("build", ASCENDING), ("hgnc_id", ASCENDING)],
            name="build_hgncid",
        ),
        IndexModel(
            [("build", ASCENDING), ("aliases", ASCENDING)],
            name="build_aliases",
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
                ("variant_type", ASCENDING),
                ("variant_rank", ASCENDING),
                ("hgnc_ids", ASCENDING),
            ],
            name="caseid_category_varianttype_variantrank_hgncids",
        ),
        IndexModel(
            [
                ("hgnc_symbols", ASCENDING),
                ("rank_score", DESCENDING),
                ("category", ASCENDING),
                ("variant_type", ASCENDING),
            ],
            name="hgncsymbol_rankscore_category_varianttype",
            partialFilterExpression={"rank_score": {"$gt": 5}, "category": "snv"},
        ),
        IndexModel(
            [
                ("hgnc_symbols", ASCENDING),
                ("rank_score", DESCENDING),
                ("category", ASCENDING),
                ("variant_type", ASCENDING),
            ],
            name="sv_hgncsymbol_rankscore_category_varianttype",
            partialFilterExpression={"rank_score": {"$gt": 5}, "category": "sv"},
        ),
        IndexModel(
            [
                ("variant_id", ASCENDING),
                ("case_id", ASCENDING),
                ("category", ASCENDING),
            ],
            name="variantid_caseid_category",
        ),
        IndexModel(
            [
                ("category", ASCENDING),
                ("case_id", ASCENDING),
                ("variant_type", ASCENDING),
                ("rank_score", ASCENDING),
            ],
            name="category_caseid_varianttype_rankscore",
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
        ),
        IndexModel(
            [("variant_id", ASCENDING), ("institute", ASCENDING)],
            name="variant_id_institute",
        ),
    ],
    "hpo_term": [
        IndexModel([("description", ASCENDING)], name="description"),
        IndexModel([("description", TEXT)], default_language="english", name="description_text"),
        IndexModel([("hpo_number", ASCENDING)], name="number"),
    ],
    "event": [
        IndexModel(
            [("category", ASCENDING), ("verb", ASCENDING), ("subject", ASCENDING)],
            name="category_verb_subject",
        ),
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
        )
    ],
    "exon": [
        IndexModel(
            [("build", ASCENDING), ("hgnc_id", ASCENDING)],
            name="build_hgncid",
        )
    ],
    "case": [
        IndexModel([("synopsis", TEXT)], default_language="english", name="synopsis_text"),
        IndexModel([("causatives", ASCENDING)], name="causatives"),
        IndexModel(
            [("collaborators", ASCENDING), ("status", ASCENDING), ("updated_at", ASCENDING)],
            name="collaborators_status_updated_at",
        ),
        IndexModel([("owner", ASCENDING), ("display_name", ASCENDING)], name="owner_display_name"),
    ],
    "managed_variant": [
        IndexModel(
            [("managed_variant_id", ASCENDING)],
            name="managed_variant_id",
        ),
        IndexModel(
            [("chromosome", ASCENDING), ("position", ASCENDING)],
            name="chrom_pos",
            collation=Collation(locale="en_US", numericOrdering=True),
        ),
    ],
}

ID_PROJECTION = {"_id": 1}
