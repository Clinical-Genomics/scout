from pymongo import (IndexModel, ASCENDING, DESCENDING)

INDEXES = {
    'hgnc_gene': [
        IndexModel([
            ('build', ASCENDING),
            ('chromosome', ASCENDING)],
            name="build_chromosome"),
         IndexModel([
            ('build', ASCENDING),
            ('hgnc_id', ASCENDING)],
            name="build_hgncid"),
        IndexModel([
            ('build', ASCENDING),
            ('aliases', ASCENDING)],
            name="build_aliases"),
    ],
    'variant': [
        IndexModel([
            ('case_id', ASCENDING),
            ('category', ASCENDING),
            ('rank_score', DESCENDING)],
            name="caseid_rankscore"),
        IndexModel([
            ('case_id', ASCENDING),
            ('category', ASCENDING),
            ('variant_rank', ASCENDING)],
            name="caseid_variantrank"),
        IndexModel([
            ('case_id', ASCENDING),
            ('category', ASCENDING),
            ('variant_type', ASCENDING),
            ('rank_score', DESCENDING)],
            name="caseid_category_varianttype_rankscore"),
        IndexModel([
            ('case_id', ASCENDING),
            ('category', ASCENDING),
            ('variant_id', ASCENDING)],
            name="caseid_variantid"),
        IndexModel([
            ('case_id', ASCENDING),
            ('category', ASCENDING),
            ('variant_type', ASCENDING),
            ('variant_rank', ASCENDING),
            ('panels', ASCENDING),
            ('thousand_genomes_frequency', ASCENDING)],
            name="caseid_varianttype_variantrank_panels_thousandg"),
        IndexModel([
            ('case_id', ASCENDING),
            ('category', ASCENDING),
            ('variant_type', ASCENDING),
            ('chromosome', ASCENDING),
            ('start', ASCENDING),
            ('end', ASCENDING),
        ],
            name="caseid_category_chromosome_start_end"),
    ],
    'hpo_term': [
        IndexModel([
            ('description', ASCENDING)],
            name="description"),
    ],
    'transcript': [
        IndexModel([
            ('build', ASCENDING),
            ('hgnc_id', ASCENDING),
            ('length', DESCENDING)],
            name="hgncid_length"),
    ],
    'exon': [
        IndexModel([
            ('build', ASCENDING),
            ('hgnc_id', ASCENDING)],
            name="build_hgncid"),
    ],
    'hpo_term': [
        IndexModel([
            ('hpo_number', ASCENDING)],
            name="number"),
    ],
    
}
