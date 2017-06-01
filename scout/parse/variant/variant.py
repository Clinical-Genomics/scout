import logging

from scout.utils.md5 import generate_md5_key
from .genotype import parse_genotypes
from .compound import parse_compounds
from .clnsig import parse_clnsig
from .gene import parse_genes
from .frequency import parse_frequencies
from .conservation import parse_conservations
from .ids import parse_ids
from .callers import parse_callers
from .rank_score import parse_rank_score
from .coordinates import parse_coordinates

from scout.exceptions import VcfError

logger = logging.getLogger(__name__)

def parse_variant(variant_dict, case, variant_type='clinical', rank_results_header=None):
    """Return a parsed variant

        Get all the necessary information to build a variant object

        Args:
            variant_dict(dict): A dictionary from VCFParser
            case(dict)
            variant_type(str): 'clinical' or 'research'

        Yields:
            variant(dict): Parsed variant
    """
    # These are to display how the rank score is built
    rank_results_header = rank_results_header or []
    variant = {}
    if 'info_dict' not in variant_dict:
        variant_dict['info_dict'] = {}
    # Create the ID for the variant
    case_id = case['_id']
    case_name = case['display_name']

    # Builds a dictionary with the different ids that are used
    variant['ids'] = parse_ids(variant_dict, case, variant_type)
    variant['case_id'] = case_id
    # type can be 'clinical' or 'research'
    # category is sv or snv
    # If SVTYPE is found in the info field we know it is a SV
    if variant_dict['info_dict'].get('SVTYPE'):
        variant['category'] = 'sv'
    else:
        variant['category'] = 'snv'
    #sub category is 'snv', 'indel', 'del', 'ins', 'dup', 'inv', 'cnv'
    # 'snv' and 'indel' are subcatogories of snv
    variant['sub_category'] = None

    ################# General information #################

    variant['reference'] = variant_dict['REF']
    variant['alternative'] = variant_dict['ALT']
    variant['quality'] = (None if variant_dict['QUAL'] == '.' else
                          float(variant_dict['QUAL']))
    variant['filters'] = variant_dict['FILTER'].split(';')
    variant['variant_type'] = variant_type

    # Add the dbsnp ids
    variant['dbsnp_id'] = None
    dbsnp_id = variant_dict['ID']
    if dbsnp_id != '.':
        variant['dbsnp_id'] = dbsnp_id

    # This is the id of other position in translocations
    # (only for specific svs)
    variant['mate_id'] = None

    ################# Position specific #################
    variant['chromosome'] = variant_dict['CHROM']
    # position = start
    variant['position'] = int(variant_dict['POS'])

    svtype = variant_dict['info_dict'].get('SVTYPE')
    if svtype:
        svtype = svtype[0].lower()

    svlen = variant_dict['info_dict'].get('SVLEN')
    if svlen:
        svlen = svlen[0]

    end = variant_dict['info_dict'].get('END')
    if end:
        end = end[0]

    mate_id = variant_dict['info_dict'].get('MATEID')
    if mate_id:
        mate_id = mate_id[0]

    coordinates = parse_coordinates(
        ref=variant['reference'],
        alt=variant['alternative'],
        position=variant['position'],
        category=variant['category'],
        svtype=svtype,
        svlen=svlen,
        end=end,
        mate_id=mate_id,
    )

    variant['sub_category'] = coordinates['sub_category']
    variant['mate_id'] = coordinates['mate_id']
    variant['end'] = coordinates['end']
    variant['length'] = coordinates['length']

    ################# Add the rank score #################
    # The rank score is central for displaying variants in scout.

    rank_score = parse_rank_score(variant_dict, case_name)
    variant['rank_score'] = rank_score

    ################# Add gt calls #################

    variant['samples'] = parse_genotypes(variant_dict, case)

    ################# Add the compound information #################

    variant['compounds'] = parse_compounds(
                                variant=variant_dict,
                                case=case,
                                variant_type=variant_type
                                )

    ################# Add the inheritance patterns #################

    genetic_models = variant_dict.get('genetic_models',{}).get(case_name,[])
    variant['genetic_models'] = genetic_models

    # Add the clinsig prediction
    variant['clnsig'] = parse_clnsig(variant_dict)

    ################# Add autozygosity calls if present #################

    azlength = variant_dict['info_dict'].get('AZLENGTH')
    if azlength:
        value = azlength[0]
        variant['azlength'] = int(value)

    azqual = variant_dict['info_dict'].get('AZQUAL')
    if azqual:
        value = azqual[0]
        variant['azqual'] = float(value)

    ################# Add the gene and transcript information #################

    variant['genes'] = parse_genes(variant_dict)

    hgnc_ids = set([])

    for gene in variant['genes']:
        hgnc_ids.add(gene['hgnc_id'])

    variant['hgnc_ids'] = list(hgnc_ids)

    ################# Add the frequencies #################

    variant['frequencies'] = parse_frequencies(variant_dict)
    # parse out old local observation count
    variant['local_obs_old'] = (int(variant_dict['info_dict'].get('Obs')[0])
                                if variant_dict['info_dict'].get('Obs') else
                                None)
    variant['local_obs_hom_old'] = (int(variant_dict['info_dict'].get('Hom')[0])
                                    if variant_dict['info_dict'].get('Hom') else
                                    None)

    # Add the severity predictions
    cadd = variant_dict['info_dict'].get('CADD')
    if cadd:
        value = cadd[0]
        variant['cadd_score'] = float(value)

    spidex = variant_dict['info_dict'].get('SPIDEX')
    if spidex:
        value = float(spidex[0])
        variant['spidex'] = value

    variant['conservation'] = parse_conservations(variant_dict)

    variant['callers'] = parse_callers(variant_dict)

    rank_result = variant_dict['info_dict'].get('RankResult')
    if rank_result:
        results = [int(i) for i in rank_result[0].split('|')]
        variant['rank_result'] = dict(zip(rank_results_header, results))

    return variant
