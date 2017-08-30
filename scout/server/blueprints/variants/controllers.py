# -*- coding: utf-8 -*-
import logging
import os.path

from flask import url_for, flash
from flask_mail import Message

from scout.constants import (CLINSIG_MAP, ACMG_MAP, MANUAL_RANK_OPTIONS, ACMG_OPTIONS,
                             ACMG_COMPLETE_MAP)
from scout.constants.acmg import ACMG_CRITERIA
from scout.models.event import VERBS_MAP
from scout.server.utils import institute_and_case
from .forms import CancerFiltersForm

log = logging.getLogger(__name__)


class MissingSangerRecipientError(Exception):
    pass


def variants(store, institute_obj, case_obj, variants_query, page=1, per_page=50):
    """Pre-process list of variants."""
    variant_count = variants_query.count()
    skip_count = per_page * max(page - 1, 0)
    more_variants = True if variant_count > (skip_count + per_page) else False

    return {
        'variants': (parse_variant(store, institute_obj, case_obj, variant_obj, update=True) for
                     variant_obj in variants_query.skip(skip_count).limit(per_page)),
        'more_variants': more_variants,
    }


def sv_variants(store, institute_obj, case_obj, variants_query, page, per_page=50):
    """Pre-process list of SV variants."""
    skip_count = (per_page * max(page - 1, 0))
    more_variants = True if variants_query.count() > (skip_count + per_page) else False

    return {
        'variants': (parse_variant(store, institute_obj, case_obj, variant) for variant in
                     variants_query.skip(skip_count).limit(per_page)),
        'more_variants': more_variants,
    }


def sv_variant(store, institute_id, case_name, variant_id):
    """Pre-process a SV variant entry for detail page."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)

    # fill in information for pilup view
    variant_case(store, case_obj, variant_obj)

    # frequencies
    variant_obj['frequencies'] = [
        ('1000G', variant_obj.get('thousand_genomes_frequency')),
        ('1000G (left)', variant_obj.get('thousand_genomes_frequency_left')),
        ('1000G (right)', variant_obj.get('thousand_genomes_frequency_right')),
    ]

    overlapping_snvs = (parse_variant(store, institute_obj, case_obj, variant) for variant in
                        store.overlapping(variant_obj))

    return dict(
        institute=institute_obj,
        case=case_obj,
        variant=variant_obj,
        overlapping_snvs=overlapping_snvs,
    )


def parse_variant(store, institute_obj, case_obj, variant_obj, update=False):
    """Parse information about variants."""
    has_changed = False
    compounds = variant_obj.get('compounds', [])
    if compounds:
        # Check if we need to add compound information
        if 'not_loaded' not in compounds[0]:
            new_compounds = store.update_compounds(variant_obj)
            variant_obj['compounds'] = new_compounds
            has_changed = True

        # sort compounds on combined rank score
        variant_obj['compounds'] = sorted(variant_obj['compounds'],
                                          key=lambda compound: -compound['combined_score'])

    variant_genes = variant_obj.get('genes')
    if variant_genes is not None:
        for gene_obj in variant_genes:
            if gene_obj.get('hgnc_symbol') is None:
                hgnc_gene = store.hgnc_gene(gene_obj['hgnc_id'])
                if hgnc_gene:
                    has_changed = True
                    gene_obj['hgnc_symbol'] = hgnc_gene['hgnc_symbol']

    if update and has_changed:
        variant_obj = store.update_variant(variant_obj)

    variant_obj['comments'] = store.events(institute_obj, case=case_obj,
                                           variant_id=variant_obj['variant_id'], comments=True)

    if variant_genes:
        variant_obj.update(get_predictions(variant_genes))
    for compound_obj in compounds:
        compound_obj.update(get_predictions(compound_obj['genes']))

    if isinstance(variant_obj.get('acmg_classification'), int):
        acmg_code = ACMG_MAP[variant_obj['acmg_classification']]
        variant_obj['acmg_classification'] = ACMG_COMPLETE_MAP[acmg_code]

    return variant_obj


def get_predictions(genes):
    """Get sift predictions from genes."""
    data = {
        'sift_predictions': [],
        'polyphen_predictions': [],
        'region_annotations': [],
        'functional_annotations': [],
    }
    for gene_obj in genes:
        for pred_key in data.keys():
            gene_key = pred_key[:-1]
            if len(genes) == 1:
                value = gene_obj.get(gene_key, '-')
            else:
                gene_id = gene_obj.get('hgnc_symbol') or str(gene_obj['hgnc_id'])
                value = ':'.join([gene_id, gene_obj.get(gene_key, '-')])
            data[pred_key].append(value)
    return data


def variant_case(store, case_obj, variant_obj):
    """Pre-process case for the variant view."""
    case_obj['bam_files'] = [individual['bam_file'] for individual in
                             case_obj['individuals'] if individual.get('bam_file')]
    case_obj['bai_files'] = [find_bai_file(bam_file) for bam_file in
                             case_obj['bam_files']]
    case_obj['sample_names'] = [individual['display_name'] for individual in
                                case_obj['individuals'] if individual['bam_file']]

    try:
        genes = variant_obj.get('genes', [])
        if len(genes) == 1:
            hgnc_gene_obj = store.hgnc_gene(variant_obj['genes'][0]['hgnc_id'])
            if hgnc_gene_obj:
                vcf_path = store.get_region_vcf(case_obj, gene_obj=hgnc_gene_obj)
                case_obj['region_vcf_file'] = vcf_path
            else:
                case_obj['region_vcf_file'] = None
        elif len(genes) > 1:
            chrom = variant_obj['genes'][0]['common']['chromosome']
            start = min(gene['common']['start'] for gene in variant_obj['genes'])
            end = max(gene['common']['end'] for gene in variant_obj['genes'])
            vcf_path = store.get_region_vcf(case_obj, chrom=chrom, start=start, end=end)
            case_obj['region_vcf_file'] = vcf_path
    except (SyntaxError, Exception):
        log.warning("skip VCF region for alignment view")


def find_bai_file(bam_file):
    """Find out BAI file by extension given the BAM file."""
    bai_file = bam_file.replace('.bam', '.bai')
    if not os.path.exists(bai_file):
        # try the other convention
        bai_file = "{}.bai".format(bam_file)
    return bai_file


def variant(store, institute_obj, case_obj, variant_id):
    """Pre-process a single variant."""
    default_panels = [store.panel(panel['panel_id']) for panel in
                      case_obj['panels'] if panel.get('is_default')]
    variant_obj = store.variant(variant_id, gene_panels=default_panels)
    if variant_obj is None:
        return None
    variant_case(store, case_obj, variant_obj)
    events = list(store.events(institute_obj, case=case_obj, variant_id=variant_obj['variant_id']))
    for event in events:
        event['verb'] = VERBS_MAP[event['verb']]
    other_causatives = []
    for other_variant in store.other_causatives(case_obj, variant_obj):
        case_display_name = other_variant['case_id'].split('-', 1)[-1]
        other_variant['case_display_name'] = case_display_name
        other_causatives.append(other_variant)

    variant_obj = parse_variant(store, institute_obj, case_obj, variant_obj)
    variant_obj['end_position'] = end_position(variant_obj)
    variant_obj['frequency'] = frequency(variant_obj)
    variant_obj['clinsig_human'] = (clinsig_human(variant_obj) if variant_obj.get('clnsig')
                                    else None)
    variant_obj['thousandg_link'] = thousandg_link(variant_obj)
    variant_obj['exac_link'] = exac_link(variant_obj)
    variant_obj['gnomead_link'] = gnomead_link(variant_obj)
    variant_obj['swegen_link'] = swegen_link(variant_obj)
    variant_obj['beacon_link'] = beacon_link(variant_obj)
    variant_obj['ucsc_link'] = ucsc_link(variant_obj)
    variant_obj['alamut_link'] = alamut_link(variant_obj)
    variant_obj['spidex_human'] = spidex_human(variant_obj)
    variant_obj['expected_inheritance'] = expected_inheritance(variant_obj)
    variant_obj['callers'] = callers(variant_obj)

    for gene_obj in variant_obj.get('genes', []):
        parse_gene(gene_obj)

    individuals = {individual['individual_id']: individual for individual in
                   case_obj['individuals']}
    for sample_obj in variant_obj['samples']:
        individual = individuals[sample_obj['sample_id']]
        sample_obj['is_affected'] = True if individual['phenotype'] == 2 else False

    gene_models = set()
    variant_obj['disease_associated_transcripts'] = []
    for gene_obj in variant_obj.get('genes', []):
        omim_models = set()
        for disease_term in gene_obj.get('disease_terms', []):
            omim_models.update(disease_term.get('inheritance', []))
        gene_obj['omim_inheritance'] = list(omim_models)
        for transcript_obj in gene_obj['transcripts']:
            if transcript_obj.get('is_disease_associated'):
                hgnc_symbol = (gene_obj['common']['hgnc_symbol'] if gene_obj['common'] else
                               gene_obj['hgnc_id'])
                refseq_ids = ', '.join(transcript_obj['refseq_ids'])
                transcript_str = "{}:{}".format(hgnc_symbol, refseq_ids)
                variant_obj['disease_associated_transcripts'].append(transcript_str)
        gene_models = gene_models | omim_models

    variant_models = set(model.split('_', 1)[0] for model in variant_obj['genetic_models'])
    variant_obj['is_matching_inheritance'] = variant_models & gene_models

    evaluations = []
    for evaluation_obj in store.get_evaluations(variant_obj):
        evaluation(store, evaluation_obj)
        evaluations.append(evaluation_obj)
    return {
        'variant': variant_obj,
        'causatives': other_causatives,
        'events': events,
        'overlapping_svs': (parse_variant(store, institute_obj, case_obj, variant_obj) for
                            variant_obj in store.overlapping(variant_obj)),
        'manual_rank_options': MANUAL_RANK_OPTIONS,
        'ACMG_OPTIONS': ACMG_OPTIONS,
        'evaluations': evaluations,
    }


def observations(store, loqusdb, case_obj, variant_obj):
    """Query observations for a variant."""
    composite_id = ("{this[chromosome]}_{this[position]}_{this[reference]}_"
                    "{this[alternative]}".format(this=variant_obj))
    obs_data = loqusdb.get_variant({'_id': composite_id}) or {}
    obs_data['total'] = loqusdb.case_count()

    obs_data['cases'] = []
    institute_id = variant_obj['institute']
    for case_id in obs_data.get('families', []):
        if case_id != variant_obj['case_id'] and case_id.startswith(institute_id):
            other_variant = store.variant(variant_obj['variant_id'], case_id=case_id)
            other_case = store.case(case_id)
            obs_data['cases'].append(dict(case=other_case, variant=other_variant))

    return obs_data


def parse_gene(gene_obj):
    """Parse variant genes."""
    if gene_obj['common']:
        ensembl_id = gene_obj['common']['ensembl_id']
        ensembl_link = ("http://grch37.ensembl.org/Homo_sapiens/Gene/Summary?"
                        "db=core;g={}".format(ensembl_id))
        gene_obj['ensembl_link'] = ensembl_link
        gene_obj['hpa_link'] = ("http://www.proteinatlas.org/search/{}".format(ensembl_id))
        gene_obj['string_link'] = ("http://string-db.org/newstring_cgi/show_network_"
                                   "section.pl?identifier={}".format(ensembl_id))
        gene_obj['entrez_link'] = ("https://www.ncbi.nlm.nih.gov/gene/{}"
                                   .format(gene_obj['common']['entrez_id']))

        reactome_link = ("http://www.reactome.org/content/query?q={}&species=Homo+sapiens"
                         "&species=Entries+without+species&cluster=true".format(ensembl_id))
        gene_obj['reactome_link'] = reactome_link
        gene_obj['expression_atlas_link'] = "https://www.ebi.ac.uk/gxa/genes/{}".format(ensembl_id)

    for tx_obj in gene_obj['transcripts']:
        parse_transcript(gene_obj, tx_obj)


def parse_transcript(gene_obj, tx_obj):
    """Parse variant gene transcript (VEP)."""
    ensembl_tx_id = tx_obj['transcript_id']
    tx_obj['ensembl_link'] = ("http://grch37.ensembl.org/Homo_sapiens/"
                              "Gene/Summary?t={}".format(ensembl_tx_id))

    tx_obj['refseq_links'] = [{
        'link': "http://www.ncbi.nlm.nih.gov/nuccore/{}".format(refseq_id),
        'id': refseq_id,
    } for refseq_id in tx_obj.get('refseq_ids', [])]

    tx_obj['swiss_prot_link'] = ("http://www.uniprot.org/uniprot/{}"
                                 .format(tx_obj['swiss_prot']))

    tx_obj['pfam_domain_link'] = ("http://pfam.xfam.org/family/{}"
                                  .format(tx_obj.get('pfam_domain')))

    tx_obj['prosite_profile_link'] = ("http://prosite.expasy.org/cgi-bin/prosite/"
                                      "prosite-search-ac?{}"
                                      .format(tx_obj.get('prosite_profile')))

    tx_obj['smart_domain_link'] = ("http://smart.embl.de/smart/search.cgi?keywords={}"
                                   .format(tx_obj.get('smart_domain')))

    if tx_obj.get('refseq_ids'):
        gene_name = (gene_obj['common']['hgnc_symbol'] if gene_obj['common'] else
                     gene_obj['hgnc_id'])
        tx_obj['change_str'] = transcript_str(tx_obj, gene_name)


def transcript_str(transcript_obj, gene_name=None):
    """Generate amino acid change as a string."""
    if transcript_obj.get('exon'):
        gene_part, part_count_raw = 'exon', transcript_obj['exon']
    elif transcript_obj.get('intron'):
        gene_part, part_count_raw = 'intron', transcript_obj['intron']
    else:
        # variant between genes
        gene_part, part_count_raw = 'intergenic', '0'

    part_count = part_count_raw.rpartition('/')[0]
    change_str = "{}:{}{}:{}:{}".format(
        ','.join(transcript_obj['refseq_ids']),
        gene_part,
        part_count,
        transcript_obj.get('coding_sequence_name', 'NA'),
        transcript_obj.get('protein_sequence_name', 'NA'),
    )
    if gene_name:
        change_str = "{}:".format(gene_name) + change_str
    return change_str


def end_position(variant_obj):
    """Calculate end position for a variant."""
    alt_bases = len(variant_obj['alternative'])
    num_bases = max(len(variant_obj['reference']), alt_bases)
    return variant_obj['position'] + (num_bases - 1)


def frequency(variant_obj):
    """Returns a judgement on the overall frequency of the variant.

    Combines multiple metrics into a single call.
    """
    most_common_frequency = max(variant_obj.get('thousand_genomes_frequency') or 0,
                                variant_obj.get('exac_frequency') or 0)
    if most_common_frequency > .05:
        return 'common'
    elif most_common_frequency > .01:
        return 'uncommon'
    else:
        return 'rare'


def clinsig_human(variant_obj):
    """Convert to human readable version of CLINSIG evaluation."""
    for clinsig_obj in variant_obj['clnsig']:
        human_str = CLINSIG_MAP.get(clinsig_obj['value'], 'not provided')
        clinsig_obj['human'] = human_str
        clinsig_obj['link'] = ("https://www.ncbi.nlm.nih.gov/clinvar/{}"
                               .format(clinsig_obj['accession']))
        yield clinsig_obj


def thousandg_link(variant_obj):
    """Compose link to 1000G page for detailed information."""
    dbsnp_id = variant_obj.get('dbsnp_id')
    if dbsnp_id:
        url_template = ("http://browser.1000genomes.org/Homo_sapiens/"
                        "Variation/Population?db=core;source=dbSNP;v={}")
        return url_template.format(dbsnp_id)
    else:
        return None


def exac_link(variant_obj):
    """Compose link to ExAC website for a variant position."""
    url_template = ("http://exac.broadinstitute.org/variant/"
                    "{this[chromosome]}-{this[position]}-{this[reference]}"
                    "-{this[alternative]}")
    return url_template.format(this=variant_obj)


def gnomead_link(variant_obj):
    """Compose link to gnomeAD website."""
    url_template = ("http://gnomad.broadinstitute.org/variant/{this[chromosome]}-"
                    "{this[position]}-{this[reference]}-{this[alternative]}")
    return url_template.format(this=variant_obj)


def swegen_link(variant_obj):
    """Compose link to SweGen Variant Frequency Database."""
    url_template = ("https://swegen-exac.nbis.se/variant/{this[chromosome]}-"
                    "{this[position]}-{this[reference]}-{this[alternative]}")
    return url_template.format(this=variant_obj)


def beacon_link(variant_obj):
    """Compose link to Beacon Network."""
    url_template = ("https://beacon-network.org/#/search?pos={this[position]}&"
                    "chrom={this[chromosome]}&allele={this[alternative]}&"
                    "ref={this[reference]}&rs=GRCh37")
    return url_template.format(this=variant_obj)


def ucsc_link(variant_obj):
    """Compose link to UCSC."""
    url_template = ("http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg19&"
                    "position=chr{this[chromosome]}:{this[position]}"
                    "-{this[position]}&dgv=pack&knownGene=pack&omimGene=pack")
    return url_template.format(this=variant_obj)


def alamut_link(variant_obj):
    url_template = ("http://localhost:10000/show?request={this[chromosome]}:"
                    "{this[position]}{this[reference]}>{this[alternative]}")
    return url_template.format(this=variant_obj)


def spidex_human(variant_obj):
    """Translate SPIDEX annotation to human readable string."""
    if variant_obj.get('spidex') is None:
        return 'not_reported'
    elif abs(variant_obj['spidex']) < 1:
        return 'low'
    elif abs(variant_obj['spidex']) < 2:
        return 'medium'
    else:
        return 'high'


def expected_inheritance(variant_obj):
    """Gather information from common gene information."""
    manual_models = set()
    for gene in variant_obj.get('genes', []):
        manual_models.update(gene.get('manual_inheritance', []))
    return list(manual_models)


def callers(variant_obj):
    """Return call for all callers."""
    calls = [('GATK', variant_obj.get('gatk', 'NA')),
             ('Samtools', variant_obj.get('samtools', 'NA')),
             ('Freebayes', variant_obj.get('freebayes', 'NA'))]
    existing_calls = [(name, caller) for name, caller in calls if caller]
    return existing_calls


def sanger(store, mail, institute_obj, case_obj, user_obj, variant_obj, sender):
    """Send Sanger email."""
    variant_link = url_for('variants.variant', institute_id=institute_obj['_id'],
                           case_name=case_obj['display_name'],
                           variant_id=variant_obj['_id'])
    if 'suspects' in case_obj and variant_obj['_id'] not in case_obj['suspects']:
        store.pin_variant(institute_obj, case_obj, user_obj, variant_link, variant_obj)

    recipients = institute_obj['sanger_recipients']
    if len(recipients) == 0:
        raise MissingSangerRecipientError()

    hgnc_symbol = ', '.join(variant_obj['hgnc_symbols'])
    gtcalls = ["<li>{}: {}</li>".format(sample_obj['display_name'],
                                        sample_obj['genotype_call'])
               for sample_obj in variant_obj['samples']]
    tx_changes = []
    for gene_obj in variant_obj.get('genes', []):
        for transcript_obj in gene_obj['transcripts']:
            parse_transcript(gene_obj, transcript_obj)
            if transcript_obj.get('change_str'):
                tx_changes.append("<li>{}</li>".format(transcript_obj['change_str']))

    html = """
      <ul">
        <li>
          <strong>Case {case_name}</strong>: <a href="{url}">{variant_id}</a>
        </li>
        <li><strong>HGNC symbols</strong>: {hgnc_symbol}</li>
        <li><strong>Gene panels</strong>: {panels}</li>
        <li><strong>GT call</strong></li>
        {gtcalls}
        <li><strong>Amino acid changes</strong></li>
        {tx_changes}
        <li><strong>Ordered by</strong>: {name}</li>
      </ul>
    """.format(case_name=case_obj['display_name'],
               url=variant_link,
               variant_id=variant_obj['display_name'],
               hgnc_symbol=hgnc_symbol,
               panels=', '.format(variant_obj['panels']),
               gtcalls=''.join(gtcalls),
               tx_changes=''.join(tx_changes),
               name=user_obj['name'].encode('utf-8'))

    kwargs = dict(subject="SCOUT: Sanger sequencing of {}".format(hgnc_symbol),
                  html=html, sender=sender, recipients=recipients,
                  # cc the sender of the email for confirmation
                  cc=[user_obj['email']])

    # compose and send the email message
    message = Message(**kwargs)
    mail.send(message)

    store.order_sanger(institute_obj, case_obj, user_obj, variant_link, variant_obj)


def cancer_variants(store, request_args, institute_id, case_name):
    """Fetch data related to cancer variants for a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    form = CancerFiltersForm(request_args)
    variants_query = store.variants(case_obj['_id'], category='cancer', query=form.data).limit(50)
    data = dict(
        institute=institute_obj,
        case=case_obj,
        variants=(parse_variant(store, institute_obj, case_obj, variant, update=True) for
                  variant in variants_query),
        form=form,
        variant_type=request_args.get('variant_type', 'clinical'),
    )
    return data


def variant_acmg(store, institute_id, case_name, variant_id):
    """Collect data relevant for rendering ACMG classification form."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    return dict(institute=institute_obj, case=case_obj, variant=variant_obj,
                CRITERIA=ACMG_CRITERIA, ACMG_OPTIONS=ACMG_OPTIONS)


def variant_acmg_post(store, institute_id, case_name, variant_id, user_email, criteria):
    """Calculate an ACMG classification based on a list of criteria."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    user_obj = store.user(user_email)
    variant_link = url_for('variants.variant', institute_id=institute_id,
                           case_name=case_name, variant_id=variant_id)
    classification = store.submit_evaluation(
        institute_obj=institute_obj,
        case_obj=case_obj,
        variant_obj=variant_obj,
        user_obj=user_obj,
        link=variant_link,
        criteria=criteria,
    )
    return classification


def evaluation(store, evaluation_obj):
    """Fetch and fill-in evaluation object."""
    evaluation_obj['institute'] = store.institute(evaluation_obj['institute_id'])
    evaluation_obj['case'] = store.case(evaluation_obj['case_id'])
    evaluation_obj['variant'] = store.variant(evaluation_obj['variant_specific'])
    evaluation_obj['criteria'] = {criterion['term']: criterion for criterion in
                                  evaluation_obj['criteria']}
    evaluation_obj['classification'] = ACMG_COMPLETE_MAP[evaluation_obj['classification']]
    return evaluation_obj


def upload_panel(store, institute_id, case_name, stream):
    """Parse out HGNC symbols from a stream."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    raw_symbols = [line.strip().split('\t')[0] for line in stream if
                   line and not line.startswith('#')]
    # check if supplied gene symbols exist
    hgnc_symbols = []
    for raw_symbol in raw_symbols:
        if store.hgnc_genes(raw_symbol).count() == 0:
            flash("HGNC symbol not found: {}".format(raw_symbol), 'warning')
        else:
            hgnc_symbols.append(raw_symbol)
    return hgnc_symbols
