# -*- coding: utf-8 -*-
from flask import url_for
from flask_mail import Message

from scout.constants import CLINSIG_MAP

MANUAL_RANK_OPTIONS = [0, 1, 2, 3, 4, 5]


class MissingSangerRecipientError(Exception):
    pass


def variants(store, variants_query, page=1, per_page=50):
    """Pre-process list of variants."""
    variant_count = variants_query.count()
    skip_count = per_page * max(page - 1, 0)
    more_variants = True if variant_count > (skip_count + 50) else False

    return {
        'variants': (parse_variant(variant_obj) for variant_obj in
                     variants_query.skip(skip_count).limit(per_page)),
        'more_variants': more_variants,
    }


def parse_variant(variant_obj):
    """Parse information about variants."""
    variant_genes = variant_obj.get('genes')
    if variant_genes is not None:
        gene_data = get_predictions(variant_genes)
        variant_obj.update(gene_data)
    return variant_obj


def get_predictions(genes):
    """Get sift predictions from genes."""
    data = {
        'sift_predictions': [],
        'polyphen_predictions': [],
        'region_annotations': [],
        'functional_annotations': [],
    }
    for gene in genes:
        for pred_key in data.keys():
            gene_key = pred_key[:-1]
            if len(genes) == 1:
                value = gene.get(gene_key, '-')
            else:
                value = ':'.join([gene['hgnc_symbol'], gene.get(gene_key, '-')])
            data[pred_key].append(value)
    return data


def variant(store, institute_obj, case_obj, variant_id):
    """Pre-process a single variant."""
    default_panels = [store.panel(panel['panel_id']) for panel in
                      case_obj['panels'] if panel.get('is_default')]
    variant_obj = store.variant(variant_id, gene_panels=default_panels)
    comments = store.events(institute_obj, case=case_obj,
                            variant_id=variant_obj['variant_id'],
                            comments=True)
    events = store.events(institute_obj, case=case_obj,
                          variant_id=variant_obj['variant_id'])
    other_causatives = []
    for other_variant in store.other_causatives(case_obj, variant_obj):
        case_display_name = other_variant['case_id'].split('-', 1)[-1]
        other_variant['case_display_name'] = case_display_name
        other_causatives.append(other_variant)

    variant_obj = parse_variant(variant_obj)
    variant_obj['end_position'] = end_position(variant_obj)
    variant_obj['frequency'] = frequency(variant_obj)
    variant_obj['clinsig_human'] = clinsig_human(variant_obj)
    variant_obj['thousandg_link'] = thousandg_link(variant_obj)
    variant_obj['exac_link'] = exac_link(variant_obj)
    variant_obj['spidex_human'] = spidex_human(variant_obj)
    variant_obj['expected_inheritance'] = expected_inheritance(variant_obj)
    variant_obj['incomplete_penetrance'] = incomplete_penetrance(variant_obj)
    variant_obj['callers'] = callers(variant_obj)

    for gene_obj in variant_obj['genes']:
        parse_gene(gene_obj)

    individuals = {individual['individual_id']: individual for individual in
                   case_obj['individuals']}
    for sample_obj in variant_obj['samples']:
        individual = individuals[sample_obj['sample_id']]
        sample_obj['is_affected'] = True if individual['phenotype'] == 2 else False

    return {
        'variant': variant_obj,
        'causatives': other_causatives,
        'comments': comments,
        'events': events,
        'overlapping_svs': store.overlapping(variant_obj),
        'manual_rank_options': MANUAL_RANK_OPTIONS,
    }


def parse_gene(gene_obj):
    """Parse variant genes."""
    ensembl_id = gene_obj['common']['ensembl_id']
    ensembl_link = ("http://grch37.ensembl.org/Homo_sapiens/Gene/Summary?"
                    "db=core;g={}".format(ensembl_id))
    gene_obj['ensembl_link'] = ensembl_link
    gene_obj['hpa_link'] = ("http://www.proteinatlas.org/search/{}".format(ensembl_id))
    gene_obj['string_link'] = ("http://string-db.org/newstring_cgi/show_network_"
                               "section.pl?identifier={}".format(ensembl_id))
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
    } for refseq_id in tx_obj.get('ref_seq', [])]

    tx_obj['swiss_prot_link'] = ("http://www.uniprot.org/uniprot/{}"
                                 .format(tx_obj['swiss_prot']))

    tx_obj['pfam_domain_link'] = ("http://pfam.xfam.org/family/{}"
                                  .format(tx_obj.get('pfam_domain')))

    tx_obj['prosite_profile_link'] = ("http://prosite.expasy.org/cgi-bin/prosite/"
                                      "prosite-search-ac?{}"
                                      .format(tx_obj.get('prosite_profile')))

    tx_obj['smart_domain_link'] = ("http://smart.embl.de/smart/search.cgi?keywords={}"
                                   .format(tx_obj.get('smart_domain')))

    if tx_obj.get('ref_seq'):
        gene_name = gene_obj['common']['hgnc_symbol']
        tx_obj['change_str'] = transcript_str(tx_obj, gene_name)


def transcript_str(transcript_obj, gene_name=None):
    """Generate amino acid change as a string."""
    change_str = "{}:exon{}:{}:{}".format(
        ','.join(transcript_obj['ref_seq']),
        transcript_obj.get('exon', '').rpartition('/')[0],
        transcript_obj['coding_sequence_name'],
        transcript_obj['protein_sequence_name'],
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
        human_str = CLINSIG_MAP.get(clinsig_obj.value, 'not provided')
        yield clinsig_obj, human_str


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
    all_models = set()
    for gene in variant_obj['genes']:
        for model in gene['common']['inheritance_models']:
            all_models.add(model)
    return list(all_models)


def incomplete_penetrance(variant_obj):
    """Return gene marked as low penetrance."""
    for gene_obj in variant_obj['genes']:
        yield {
            'hgnc_symbol': gene_obj['common']['hgnc_symbol'],
            'omim': gene_obj.get('omim_penetrance'),
            'manual': gene_obj.get('manual_penetrance'),
        }


def callers(variant_obj):
    """Return call for all callers."""
    calls = [('GATK', variant_obj['gatk']), ('Samtools', variant_obj['samtools']),
             ('Freebayes', variant_obj['freebayes'])]
    existing_calls = [(name, caller) for name, caller in calls if caller]
    return existing_calls


def sanger(store, mail, institute_obj, case_obj, user_obj, variant_obj, sender):
    """Send Sanger email."""
    variant_link = url_for('variants.variant', institute_id=institute_obj['_id'],
                           case_name=case_obj['display_name'],
                           variant_id=variant_obj['_id'])
    if variant_obj['_id'] not in case_obj['suspects']:
        store.pin_variant(institute_obj, case_obj, user_obj, variant_link, variant_obj)

    recipients = institute_obj['sanger_recipients']
    if len(recipients) == 0:
        raise MissingSangerRecipientError()

    hgnc_symbol = ', '.join(variant_obj['hgnc_symbols'])
    gtcalls = ["<li>{}: {}</li>".format(sample_obj['display_name'],
                                        sample_obj['genotype_call'])
               for sample_obj in variant_obj['samples']]
    tx_changes = []
    for gene_obj in variant_obj['genes']:
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
