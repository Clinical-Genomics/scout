from pymongo import (IndexModel, ASCENDING, DESCENDING, TEXT)

INDEXES = {
    'hgnc_gene': [
        IndexModel([
            ('build', ASCENDING),
            ('chromosome', ASCENDING)],
            name="build_chromosome",
            background=True,
            ),
         IndexModel([
            ('build', ASCENDING),
            ('hgnc_id', ASCENDING)],
            name="build_hgncid",
            background=True,
            ),
        IndexModel([
            ('build', ASCENDING),
            ('aliases', ASCENDING)],
            name="build_aliases",
            background=True,
            ),
    ],
    'variant': [
        IndexModel([
            ('case_id', ASCENDING),
            ('category', ASCENDING),
            ('rank_score', DESCENDING)],
            name="caseid_rankscore",
            background=True,
            ),
        IndexModel([
            ('case_id', ASCENDING),
            ('category', ASCENDING),
            ('variant_rank', ASCENDING)],
            name="caseid_variantrank",
            background=True,
            ),
        IndexModel([
            ('case_id', ASCENDING),
            ('category', ASCENDING),
            ('variant_type', ASCENDING),
            ('rank_score', DESCENDING)],
            name="caseid_category_varianttype_rankscore",
            background=True,
            ),
        IndexModel([
            ('case_id', ASCENDING),
            ('category', ASCENDING),
            ('variant_id', ASCENDING)],
            name="caseid_variantid",
            background=True,
            ),
        IndexModel([
            ('case_id', ASCENDING),
            ('category', ASCENDING),
            ('variant_type', ASCENDING),
            ('variant_rank', ASCENDING),
            ('panels', ASCENDING),
            ('thousand_genomes_frequency', ASCENDING)],
            name="caseid_varianttype_variantrank_panels_thousandg",
            background=True,
            ),
        IndexModel([
            ('case_id', ASCENDING),
            ('category', ASCENDING),
            ('variant_type', ASCENDING),
            ('chromosome', ASCENDING),
            ('start', ASCENDING),
            ('end', ASCENDING),],
            name="caseid_category_chromosome_start_end",
            background=True,
            ),
    ],
    'hpo_term': [
        IndexModel([
            ('description', ASCENDING)],
            name="description"),
        IndexModel([
            ('description', TEXT)],
            default_language='english',
            name="description_text"),
        IndexModel([
            ('hpo_number', ASCENDING)],
            name="number"),
    ],
    'transcript': [
        IndexModel([
            ('build', ASCENDING),
            ('hgnc_id', ASCENDING),
            ('length', DESCENDING)],
            name="hgncid_length",
            background=True,
            ),
    ],
    'exon': [
        IndexModel([
            ('build', ASCENDING),
            ('hgnc_id', ASCENDING)],
            name="build_hgncid",
            background=True,
            ),
    ],
    'hpo_term': [
        IndexModel([
            ('hpo_number', ASCENDING)],
            name="number",
            background=True,
            ),
    ],
    
}

