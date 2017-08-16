import logging

from datetime import datetime

from cyvcf2 import VCF

from scout.parse.variant import parse_variant
from scout.build import build_variant
from scout.exceptions import IntegrityError
from scout.parse.variant.rank_score import parse_rank_score

from scout.parse.variant.headers import (parse_rank_results_header, parse_vep_header)

logger = logging.getLogger(__name__)


def delete_variants(adapter, case_obj, variant_type='clinical'):
    """Delete all variants for a case of a certain variant type

        Args:
            case_obj(dict)
            variant_type(str)
    """
    adapter.delete_variants(case_id=case_obj['_id'], variant_type=variant_type)


def check_coordinates(variant, coordinates):
    """Check if the variant is in the interval given by the coordinates

        Args:
            variant(dict)
            coordinates
    """
    if variant['chromosome'] == coordinates['chrom']:
        pos = variant['position']
        if (pos >= coordinates['start'] and pos <= coordinates['end']):
            return True
    return False


def load_variants(adapter, variant_file, case_obj, variant_type='clinical',
                  category='snv', rank_threshold=5, chrom=None, start=None,
                  end=None):
    """Load all variant in variants

        Args:
            adapter(MongoAdapter)
            variant_file(str): Path to variant file
            case(Case)
            variant_type(str)
            category(str): 'snv' or 'sv'
            rank_threshold(int)
            chrom(str)
            start(int)
            end(int)
    """

    institute_obj = adapter.institute(institute_id=case_obj['owner'])

    if not institute_obj:
        raise IntegrityError("Institute {0} does not exist in"
                             " database.".format(case_obj['owner']))

    gene_to_panels = adapter.gene_to_panels()

    hgncid_to_gene = adapter.hgncid_to_gene()

    coordinates = {}

    vcf_obj = VCF(variant_file)

    rank_results_header = parse_rank_results_header(vcf_obj)
    vep_header = parse_vep_header(vcf_obj)

    # This is a dictionary to tell where ind are in vcf
    individual_positions = {}
    for i,ind in enumerate(vcf_obj.samples):
        individual_positions[ind] = i

    logger.info("Start inserting variants into database")
    start_insertion = datetime.now()
    start_five_thousand = datetime.now()
    nr_variants = 0
    nr_inserted = 0
    inserted = 1

    coordinates = False
    if chrom:
        coordinates = {
            'chrom': chrom,
            'start': start,
            'end': end
        }

    try:
        for nr_variants, variant in enumerate(vcf_obj):
            rank_score = parse_rank_score(
                variant.INFO.get('RankScore'),
                case_obj['display_name']
            )
            variant_obj = None
            add_variant = False

            if coordinates or (rank_score > rank_threshold):
                parsed_variant = parse_variant(
                    variant=variant,
                    case=case_obj,
                    variant_type=variant_type,
                    rank_results_header=rank_results_header,
                    vep_header = vep_header,
                    individual_positions = individual_positions
                )
                add_variant = True
                # If there are coordinates the variant should be loaded
                if coordinates:
                    if not check_coordinates(parsed_variant, coordinates):
                        add_variant = False

                if add_variant:
                    variant_obj = build_variant(
                        variant=parsed_variant,
                        institute_id=institute_obj['_id'],
                        gene_to_panels=gene_to_panels,
                        hgncid_to_gene=hgncid_to_gene,
                    )
                    try:
                        load_variant(adapter, variant_obj)
                        nr_inserted += 1
                    except IntegrityError as error:
                        pass

                if (nr_variants != 0 and nr_variants % 5000 == 0):
                    logger.info("%s variants parsed" % str(nr_variants))
                    logger.info("Time to parse variants: {} ".format(
                                datetime.now() - start_five_thousand))
                    start_five_thousand = datetime.now()

                if (nr_inserted != 0 and (nr_inserted * inserted) % (1000 * inserted) == 0):
                    logger.info("%s variants inserted" % nr_inserted)
                    inserted += 1

    except Exception as error:
        if not coordinates:
            logger.warning("Deleting inserted variants")
            delete_variants(adapter, case_obj, variant_type)
        raise error

    logger.info("All variants inserted.")
    logger.info("Number of variants in file: {0}".format(nr_variants + 1))
    logger.info("Number of variants inserted: {0}".format(nr_inserted))
    logger.info("Time to insert variants:{0}".format(datetime.now() - start_insertion))

    # This function will add a variant rank and add information on compound objects
    # adapter.update_variants(case_obj, variant_type, category=category)


def load_variant(adapter, variant_obj):
    """Load a variant into the database

        Parse the variant, create a variant object and load it into
        the database.

        Args:
            adapter(MongoAdapter)
            variant_obj(scout.models.Variant)

    """
    variant_id = adapter.load_variant(variant_obj)
    return variant_id
