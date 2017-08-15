import logging

from pprint import pprint as pp

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
from .models import parse_genetic_models
from .transcript import parse_transcripts
from .deleteriousness import parse_cadd

from scout.exceptions import VcfError

logger = logging.getLogger(__name__)

def parse_variant(variant, case, variant_type='clinical',
                 rank_results_header=None, vep_header=None,
                 individual_positions=None, category=None):
    """Return a parsed variant

        Get all the necessary information to build a variant object

    Args:
        variant(cyvcf2.Variant)
        case(dict)
        variant_type(str): 'clinical' or 'research'
        rank_results_header(list)
        vep_header(list)
        individual_positions(dict): Explain what position each individual has
                                    in vcf
        category(str): 'snv', 'sv' or 'cancer'

    Returns:
        parsed_variant(dict): Parsed variant
    """
    # These are to display how the rank score is built
    rank_results_header = rank_results_header or []
    # Vep information
    vep_header = vep_header or []

    parsed_variant = {}

    # Create the ID for the variant
    case_id = case['_id']
    case_name = case['display_name']

    chrom = variant.CHROM
    if (chrom.startswith('chr') or chrom.startswith('CHR')):
        chrom = chrom[3:]
    # Builds a dictionary with the different ids that are used
    parsed_variant['ids'] = parse_ids(
        chrom=chrom,
        pos=variant.POS,
        ref=variant.REF,
        alt=variant.ALT[0],
        case_id=case_id,
        variant_type=variant_type
    )
    parsed_variant['case_id'] = case_id
    # type can be 'clinical' or 'research'
    parsed_variant['variant_type'] = variant_type
    # category is sv or snv
    # cyvcf2 knows if it is a sv, indel or snv variant
    if not category:
        category = variant.var_type
        if category == 'indel':
            category = 'snv'
        if category == 'snp':
            category = 'snv'

    parsed_variant['category'] = category
    #sub category is 'snv', 'indel', 'del', 'ins', 'dup', 'inv', 'cnv'
    # 'snv' and 'indel' are subcatogories of snv
    parsed_variant['sub_category'] = None

    ################# General information #################

    parsed_variant['reference'] = variant.REF
    # We allways assume splitted and normalized vcfs
    if len(variant.ALT) > 1:
        raise VcfError("Variants are only allowed to have one alternative")
    parsed_variant['alternative'] = variant.ALT[0]

    # cyvcf2 will set QUAL to None if '.' in vcf
    parsed_variant['quality'] = variant.QUAL
    if variant.FILTER:
        parsed_variant['filters'] = variant.FILTER.split(';')
    else:
        parsed_variant['filters'] = ['PASS']

    # Add the dbsnp ids
    parsed_variant['dbsnp_id'] = variant.ID

    # This is the id of other position in translocations
    # (only for specific svs)
    parsed_variant['mate_id'] = None

    ################# Position specific #################
    parsed_variant['chromosome'] = chrom
    # position = start
    parsed_variant['position'] = int(variant.POS)

    svtype = variant.INFO.get('SVTYPE')

    svlen = variant.INFO.get('SVLEN')

    end = int(variant.end)

    mate_id = variant.INFO.get('MATEID')

    coordinates = parse_coordinates(
        chrom=parsed_variant['chromosome'],
        ref=parsed_variant['reference'],
        alt=parsed_variant['alternative'],
        position=parsed_variant['position'],
        category=parsed_variant['category'],
        svtype=svtype,
        svlen=svlen,
        end=end,
        mate_id=mate_id,
    )

    parsed_variant['sub_category'] = coordinates['sub_category']
    parsed_variant['mate_id'] = coordinates['mate_id']
    parsed_variant['end'] = int(coordinates['end'])
    parsed_variant['length'] = int(coordinates['length'])
    parsed_variant['end_chrom'] = coordinates['end_chrom']
    parsed_variant['cytoband_start'] = coordinates['cytoband_start']
    parsed_variant['cytoband_end'] = coordinates['cytoband_end']

    ################# Add the rank score #################
    # The rank score is central for displaying variants in scout.

    rank_score = parse_rank_score(variant.INFO.get('RankScore', ''), case_name)
    parsed_variant['rank_score'] = rank_score or 0

    ################# Add gt calls #################
    samples = {}
    if individual_positions:
        samples = parse_genotypes(
                            variant,
                            case,
                            individual_positions
                        )
    parsed_variant['samples'] = samples

    ################# Add the compound information #################
    compounds = parse_compounds(
                                compound_info=variant.INFO.get('Compounds'),
                                case=case,
                                variant_type=variant_type
                                )
    if compounds:
        parsed_variant['compounds'] = compounds

    ################# Add the inheritance patterns #################

    genetic_models = parse_genetic_models(variant.INFO.get('GeneticModels'), case_name)
    if genetic_models:
        parsed_variant['genetic_models'] = genetic_models

    ################# Add autozygosity calls if present #################

    azlength = variant.INFO.get('AZLENGTH')
    if azlength:
        parsed_variant['azlength'] = int(azlength)

    azqual = variant.INFO.get('AZQUAL')
    if azqual:
        parsed_variant['azqual'] = float(azqual)

    ################# Add the gene and transcript information #################
    raw_transcripts = []
    if vep_header:
        vep_info = variant.INFO.get('CSQ')
        if vep_info:
            raw_transcripts = (dict(zip(vep_header, transcript_info.split('|')))
                               for transcript_info in vep_info.split(','))


    parsed_transcripts = []
    dbsnp_ids = set()
    cosmic_ids = set()
    for parsed_transcript in parse_transcripts(raw_transcripts, parsed_variant['alternative']):
        parsed_transcripts.append(parsed_transcript)
        for dbsnp in parsed_transcript.get('dbsnp', []):
            dbsnp_ids.add(dbsnp)
        for cosmic in parsed_transcript.get('cosmic', []):
            cosmic_ids.add(cosmic)

    if (dbsnp_ids and not parsed_variant['dbsnp_id']):
        parsed_variant['dbsnp_id'] = ';'.join(dbsnp_ids)

    if cosmic_ids:
        parsed_variant['cosmic_ids'] = list(cosmic_ids)

    gene_info = parse_genes(parsed_transcripts)

    parsed_variant['genes'] = gene_info

    hgnc_ids = set([])

    for gene in parsed_variant['genes']:
        hgnc_ids.add(gene['hgnc_id'])

    parsed_variant['hgnc_ids'] = list(hgnc_ids)

    ################# Add the clinsig prediction #################
    clnsig_predictions = parse_clnsig(
        acc=variant.INFO.get('CLNACC'),
        sig=variant.INFO.get('CLNSIG'),
        revstat=variant.INFO.get('CLNREVSTAT'),
        transcripts=parsed_transcripts
        )

    if clnsig_predictions:
        parsed_variant['clnsig'] = clnsig_predictions

    ################# Add the frequencies #################
    frequencies = parse_frequencies(variant, parsed_transcripts)

    parsed_variant['frequencies'] = frequencies

    # parse out old local observation count
    local_obs_old = variant.INFO.get('Obs')
    if local_obs_old:
        parsed_variant['local_obs_old'] = int(local_obs_old)

    local_obs_hom_old = variant.INFO.get('Hom')
    if local_obs_hom_old:
        parsed_variant['local_obs_hom_old'] = int(local_obs_hom_old)

    ###################### Add the severity predictions ######################
    cadd = parse_cadd(variant, parsed_transcripts)
    if cadd:
        parsed_variant['cadd_score'] = cadd

    spidex = variant.INFO.get('SPIDEX')
    if spidex:
        parsed_variant['spidex'] = float(spidex)

    ###################### Add the conservation ######################

    parsed_variant['conservation'] = parse_conservations(variant)

    parsed_variant['callers'] = parse_callers(variant)

    rank_result = variant.INFO.get('RankResult')
    if rank_result:
        results = [int(i) for i in rank_result.split('|')]
        parsed_variant['rank_result'] = dict(zip(rank_results_header, results))

    return parsed_variant
