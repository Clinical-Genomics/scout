import logging
from vcf_parser import VCFParser

from scout.parse.variant import parse_variant
from scout.build import build_variant
from scout.exceptions import IntegrityError


logger = logging.getLogger(__name__)


def delete_variants(adapter, case_obj, variant_type='clinical'):
    """Delete all variants for a case of a certain variant type

        Args:
            case_obj(Case)
            variant_type(str)
    """
    adapter.delete_variants(
        case_id=case_obj['case_id'],
        variant_type=variant_type
    )


def load_variants(adapter, variant_file, case_obj, variant_type='clinical',
                  category='snv'):
    """Load all variantt in variants

        Args:
            adapter(MongoAdapter)
            variant_file(str): Path to variant file
            case(Case)
            variant_type(str)

    """

    institute_obj = adapter.institute(institute_id=case_obj['owner'])
    if not institute_obj:
        raise IntegrityError("Institute {0} does not exist in"
                             " database.".format(case_obj['owner']))

    hgnc_genes = {}
    for gene in adapter.all_genes():
        hgnc_genes[gene.hgnc_id] = gene

    variants = VCFParser(infile=variant_file)
    rank_results_header = []
    for info_line in variants.metadata.info_lines:
        if info_line['ID'] == 'RankResult':
            rank_results_header = info_line['Description'].split('|')

    try:
        for variant in variants:
            load_variant(
                adapter=adapter,
                variant=variant,
                case_obj=case_obj,
                institute_obj=institute_obj,
                hgnc_genes=hgnc_genes,
                variant_type=variant_type,
                rank_results_header=rank_results_header
            )
    except Exception as e:
        logger.error(e.message)
        logger.info("Deleting inserted variants")
        delete_variants(adapter, case_obj, variant_type)
        raise e

    adapter.add_variant_rank(case_obj, variant_type, category=category)


def load_variant(adapter, variant, case_obj, institute_obj, hgnc_genes,
                 variant_type='clinical', rank_results_header=None):
    """Load a variant into the database

        Parse the variant, create a mongoengine object and load it into
        the database.

        Args:
            adapter(MongoAdapter)
            variant(vcf_parser.Variant)
            case_obj(Case)
            institute_obj(Institute)
            hgnc_genes(dict[HgncGene])
            variant_type(str)
            rank_results_header(list)

        Returns:
            variant_obj(Variant): mongoengine Variant object
    """
    rank_results_header = rank_results_header or []
    parsed_variant = parse_variant(
        variant_dict=variant,
        case=case_obj,
        variant_type=variant_type,
        rank_results_header=rank_results_header
    )

    variant_obj = build_variant(
        variant=parsed_variant,
        institute=institute_obj,
        hgnc_genes=hgnc_genes
    )

    adapter.load_variant(variant_obj)
    return variant_obj
