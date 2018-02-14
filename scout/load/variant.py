import logging

from datetime import datetime

from cyvcf2 import VCF

from scout.parse.variant import parse_variant
from scout.build import build_variant
from scout.exceptions import IntegrityError
from scout.parse.variant.rank_score import parse_rank_score
from scout.constants import CHR_PATTERN
from scout.utils.coordinates import check_coordinates

from scout.parse.variant.headers import (parse_rank_results_header, parse_vep_header)

LOG = logging.getLogger(__name__)


def delete_variants(adapter, case_obj, variant_type='clinical'):
    """Delete all variants for a case of a certain variant type

        Args:
            case_obj(dict)
            variant_type(str)
    """
    adapter.delete_variants(case_id=case_obj['_id'], variant_type=variant_type)

def load_variants(adapter, variant_file, case_obj, variant_type='clinical',
                  category='snv', rank_threshold=6, chrom=None, start=None,
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

    LOG.info("Start inserting variants into database")
    start_insertion = datetime.now()
    start_five_thousand = datetime.now()
    # To get it right if the file is empty
    nr_variants = -1
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
            
            # Get the neccesary coordinates
            # Parse away any chr CHR prefix
            chrom_match = CHR_PATTERN.match(variant.CHROM)
            chrom = chrom_match.group(2)
            position = variant.POS

            add_variant = False
            
            # If coordinates are specified we want to upload all variants that 
            # resides within the specified region
            if coordinates:
                if check_coordinates(chrom, position, coordinates):
                    add_variant = True
            # If there are no coordinates we allways want to load MT variants
            elif chrom == 'MT':
                add_variant = True
            # Otherwise we need to check is rank score requirement are fulfilled
            else:
                rank_score = parse_rank_score(
                    variant.INFO.get('RankScore'),
                    case_obj['display_name']
                )
                if rank_score >= rank_threshold:
                    add_variant = True
            variant_obj = None

            # Log the number of variants parsed
            if (nr_variants != 0 and nr_variants % 5000 == 0):
                LOG.info("%s variants parsed" % str(nr_variants))
                LOG.info("Time to parse variants: {} ".format(
                            datetime.now() - start_five_thousand))
                start_five_thousand = datetime.now()
            
            if not add_variant:
                continue
            
            ####### Here we know that the variant should be loaded #########
            # We follow the scout paradigm of parse -> build -> load
            
            # Parse the variant
            parsed_variant = parse_variant(
                variant=variant,
                case=case_obj,
                variant_type=variant_type,
                rank_results_header=rank_results_header,
                vep_header = vep_header,
                individual_positions = individual_positions
            )

            # Build the variant object
            variant_obj = build_variant(
                variant=parsed_variant,
                institute_id=institute_obj['_id'],
                gene_to_panels=gene_to_panels,
                hgncid_to_gene=hgncid_to_gene,
            )
            
            # Load the variant abject
            # We could get integrity error here since if we want to load all variants of a region
            # there will likely already be variants from that region loaded
            try:
                load_variant(adapter, variant_obj)
                nr_inserted += 1
            except IntegrityError as error:
                pass

            # Log number of inserted variants
            if (nr_inserted != 0 and (nr_inserted * inserted) % (1000 * inserted) == 0):
                LOG.info("%s variants inserted" % nr_inserted)
                inserted += 1

    except Exception as error:
        if not coordinates:
            LOG.warning("Deleting inserted variants")
            delete_variants(adapter, case_obj, variant_type)
        raise error

    LOG.info("All variants inserted.")
    LOG.info("Number of variants in file: {0}".format(nr_variants + 1))
    LOG.info("Number of variants inserted: {0}".format(nr_inserted))
    LOG.info("Time to insert variants:{0}".format(datetime.now() - start_insertion))

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
