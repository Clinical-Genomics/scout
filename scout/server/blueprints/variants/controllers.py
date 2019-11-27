# -*- coding: utf-8 -*-
import logging
import os.path
import urllib.parse

from pprint import pprint as pp

from xlsxwriter import Workbook

from datetime import date
import datetime
from flask_login import current_user
from flask import url_for, flash, request
from flask_mail import Message
from werkzeug.datastructures import MultiDict

from scout.constants import (
    CLINSIG_MAP, ACMG_MAP, MANUAL_RANK_OPTIONS, ACMG_OPTIONS, DISMISS_VARIANT_OPTIONS,
    ACMG_COMPLETE_MAP, CALLERS, SPIDEX_HUMAN, VERBS_MAP, MOSAICISM_OPTIONS, SEVERE_SO_TERMS
)
from scout.constants.acmg import ACMG_CRITERIA
from scout.constants.variants_export import EXPORT_HEADER, VERIFIED_VARIANTS_HEADER
from scout.export.variant import export_verified_variants
from scout.server.utils import (institute_and_case, user_institutes, case_append_bam, variant_case)
from scout.server.links import (add_gene_links, ensembl, add_tx_links)
from scout.server.blueprints.genes.controllers import gene
from scout.utils.requests import fetch_refseq_version

from scout.server.blueprints.variant.utils import (predictions)
from .forms import (FiltersForm, SvFiltersForm, StrFiltersForm, CancerFiltersForm,
                    VariantFiltersForm)


LOG = logging.getLogger(__name__)

def variants(store, institute_obj, case_obj, variants_query, page=1, per_page=50):
    """Pre-process list of variants."""
    variant_count = variants_query.count()
    skip_count = per_page * max(page - 1, 0)
    more_variants = True if variant_count > (skip_count + per_page) else False
    variant_res = variants_query.skip(skip_count).limit(per_page)

    genome_build = case_obj.get('genome_build', '37')
    if genome_build not in ['37','38']:
        genome_build = '37'

    variants = []
    for variant_obj in variant_res:
        overlapping_svs = [sv for sv in store.overlapping(variant_obj)]
        variant_obj['overlapping'] = overlapping_svs or None

        # Get all previous ACMG evalautions of the variant
        evaluations = []
        for evaluation_obj in store.get_evaluations(variant_obj):
            classification = evaluation_obj['classification']
            # Only show pathogenic/likely pathogenic from other cases on variants page
            if evaluation_obj['case_id'] == case_obj['_id']:
                continue
            if not classification in ['pathogenic', 'likely_pathogenic']:
                continue
            # Convert the classification int to readable string
            evaluation_obj['classification'] = ACMG_COMPLETE_MAP.get(classification)
            evaluations.append(evaluation_obj)
        variant_obj['evaluations'] = evaluations

        variants.append(parse_variant(store, institute_obj, case_obj, variant_obj,
                        update=True, genome_build=genome_build))

    return {
        'variants': variants,
        'more_variants': more_variants,
    }

def sv_variants(store, institute_obj, case_obj, variants_query, page=1, per_page=50):
    """Pre-process list of SV variants."""
    skip_count = (per_page * max(page - 1, 0))
    more_variants = True if variants_query.count() > (skip_count + per_page) else False

    genome_build = case_obj.get('genome_build', '37')
    if genome_build not in ['37','38']:
        genome_build = '37'

    return {
        'variants': (parse_variant(store, institute_obj, case_obj, variant, genome_build=genome_build) for variant in
                     variants_query.skip(skip_count).limit(per_page)),
        'more_variants': more_variants,
    }

def str_variants(store, institute_obj, case_obj, variants_query, page=1, per_page=50):
    """Pre-process list of STR variants."""

    # Nothing unique to STRs on this level. Inheritance? yep, you will want it.

    # case bam_files for quick access to alignment view.
    case_append_bam(case_obj)

    return variants(store, institute_obj, case_obj, variants_query, page, per_page)


def parse_variant(store, institute_obj, case_obj, variant_obj, update=False, genome_build='37',
                  get_compounds = True):
    """Parse information about variants.

    - Adds information about compounds
    - Updates the information about compounds if necessary and 'update=True'

    Args:
        store(scout.adapter.MongoAdapter)
        institute_obj(scout.models.Institute)
        case_obj(scout.models.Case)
        variant_obj(scout.models.Variant)
        update(bool): If variant should be updated in database
        genome_build(str)

    """
    has_changed = False
    compounds = variant_obj.get('compounds', [])
    if compounds and get_compounds:
        # Check if we need to add compound information
        # If it is the first time the case is viewed we fill in some compound information
        if 'not_loaded' not in compounds[0]:
            new_compounds = store.update_variant_compounds(variant_obj)
            variant_obj['compounds'] = new_compounds
            has_changed = True

        # sort compounds on combined rank score
        variant_obj['compounds'] = sorted(variant_obj['compounds'],
                                          key=lambda compound: -compound['combined_score'])

    # Update the hgnc symbols if they are incorrect
    variant_genes = variant_obj.get('genes')
    if variant_genes is not None:
        for gene_obj in variant_genes:
            # If there is no hgnc id there is nothin we can do
            if not gene_obj['hgnc_id']:
                continue
            # Else we collect the gene object and check the id
            if gene_obj.get('hgnc_symbol') is None:
                hgnc_gene = store.hgnc_gene(gene_obj['hgnc_id'], build=genome_build)
                if not hgnc_gene:
                    continue
                has_changed = True
                gene_obj['hgnc_symbol'] = hgnc_gene['hgnc_symbol']

    # We update the variant if some information was missing from loading
    # Or if symbold in reference genes have changed
    if update and has_changed:
        variant_obj = store.update_variant(variant_obj)

    variant_obj['comments'] = store.events(institute_obj, case=case_obj,
                                           variant_id=variant_obj['variant_id'], comments=True)

    if variant_genes:
        variant_obj.update(predictions(variant_genes))
        if variant_obj.get('category') == 'cancer':
            variant_obj.update(get_variant_info(variant_genes))

    for compound_obj in compounds:
        compound_obj.update(predictions(compound_obj.get('genes', [])))

    classification = variant_obj.get('acmg_classification')
    if isinstance(classification, int):
        acmg_code = ACMG_MAP[variant_obj['acmg_classification']]
        variant_obj['acmg_classification'] = ACMG_COMPLETE_MAP[acmg_code]


    # convert length for SV variants
    variant_length = variant_obj.get('length')
    variant_obj['length'] = {100000000000: 'inf', -1: 'n.d.'}.get(variant_length, variant_length)
    if not 'end_chrom' in variant_obj:
        variant_obj['end_chrom'] = variant_obj['chromosome']

    return variant_obj


def variant_export_lines(store, case_obj, variants_query):
    """Get variants info to be exported to file, one list (line) per variant.

        Args:
            store(scout.adapter.MongoAdapter)
            case_obj(scout.models.Case)
            variants_query: a list of variant objects, each one is a dictionary

        Returns:
            export_variants: a list of strings. Each string  of the list corresponding to the fields
                             of a variant to be exported to file, separated by comma
    """

    export_variants = []

    for variant in variants_query:
        variant_line = []
        position = variant['position']
        change = variant['reference']+'>'+variant['alternative']
        variant_line.append(variant['rank_score'])
        variant_line.append(variant['chromosome'])
        variant_line.append(position)
        variant_line.append(change)
        variant_line.append('_'.join([str(position), change]))

        # gather gene info:
        gene_list = variant.get('genes') #this is a list of gene objects
        gene_ids = []
        gene_names = []
        hgvs_c = []

        # if variant is in genes
        if len(gene_list) > 0:
            for gene_obj in gene_list:
                hgnc_id = gene_obj['hgnc_id']
                gene_name = gene(store, hgnc_id)['symbol']

                gene_ids.append(hgnc_id)
                gene_names.append(gene_name)

                hgvs_nucleotide = '-'
                # gather HGVS info from gene transcripts
                transcripts_list = gene_obj.get('transcripts')
                for transcript_obj in transcripts_list:
                    if transcript_obj.get('is_canonical') and transcript_obj.get('is_canonical') is True:
                        hgvs_nucleotide = str(transcript_obj.get('coding_sequence_name'))
                hgvs_c.append(hgvs_nucleotide)

            variant_line.append(';'.join( str(x) for x in  gene_ids))
            variant_line.append(';'.join( str(x) for x in  gene_names))
            variant_line.append(';'.join( str(x) for x in  hgvs_c))
        else:
            while i < 4:
                variant_line.append('-') # instead of gene ids
                i = i+1

        variant_gts = variant['samples'] # list of coverage and gt calls for case samples
        for individual in case_obj['individuals']:
            for variant_gt in variant_gts:
                if individual['individual_id'] == variant_gt['sample_id']:
                    # gather coverage info
                    variant_line.append(variant_gt['allele_depths'][0]) # AD reference
                    variant_line.append(variant_gt['allele_depths'][1]) # AD alternate
                    # gather genotype quality info
                    variant_line.append(variant_gt['genotype_quality'])

        variant_line = [str(i) for i in variant_line]
        export_variants.append(",".join(variant_line))

    return export_variants


def variants_export_header(case_obj):
    """Returns a header for the CSV file with the filtered variants to be exported.

        Args:
            case_obj(scout.models.Case)

        Returns:
            header: includes the fields defined in scout.constants.variants_export EXPORT_HEADER
                    + AD_reference, AD_alternate, GT_quality for each sample analysed for a case
    """
    header = []
    header = header + EXPORT_HEADER
    # Add fields specific for case samples
    for individual in case_obj['individuals']:
        display_name = str(individual['display_name'])
        header.append('AD_reference_'+display_name) # Add AD reference field for a sample
        header.append('AD_alternate_'+display_name) # Add AD alternate field for a sample
        header.append('GT_quality_'+display_name) # Add Genotype quality field for a sample
    return header


def get_variant_info(genes):
    """Get variant information"""
    data = {'canonical_transcripts': []}
    for gene_obj in genes:
        if not gene_obj.get('canonical_transcripts'):
            tx = gene_obj['transcripts'][0]
            tx_id = tx['transcript_id']
            exon = tx.get('exon', '-')
            c_seq = tx.get('coding_sequence_name', '-')
        else:
            tx_id = gene_obj['canonical_transcripts']
            exon = gene_obj.get('exon', '-')
            c_seq = gene_obj.get('hgvs_identifier', '-')

        if len(c_seq) > 20:
            c_seq = c_seq[:20] + '...'

        if len(genes) == 1:
            value = ':'.join([tx_id,exon,c_seq])
        else:
            gene_id = gene_obj.get('hgnc_symbol') or str(gene_obj['hgnc_id'])
            value = ':'.join([gene_id, tx_id,exon,c_seq])
        data['canonical_transcripts'].append(value)

    return data

def cancer_variants(store, institute_id, case_name, form, page=1):
    """Fetch data related to cancer variants for a case."""

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    per_page = 50
    skip_count = per_page * max(page - 1, 0)
    variants_query = store.variants(case_obj['_id'], category='cancer', query=form.data)
    variant_count = variants_query.count()
    more_variants = True if variant_count > (skip_count + per_page) else False
    variant_res = variants_query.skip(skip_count).limit(per_page)
    data = dict(
        page=page,
        more_variants=more_variants,
        institute=institute_obj,
        case=case_obj,
        variants=(parse_variant(store, institute_obj, case_obj, variant, update=True) for
                  variant in variant_res),
        form=form,
    )
    return data

def get_clinvar_submission(store, institute_id, case_name, variant_id, submission_id):
    """Collects all variants from the clinvar submission collection with a specific submission_id

        Args:
            store(scout.adapter.MongoAdapter)
            institute_id(str): Institute ID
            case_name(str): case ID
            variant_id(str): variant._id
            submission_id(str): clinvar submission id, i.e. SUB76578

        Returns:
            A dictionary with all the data to display the clinvar_update.html template page
    """

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    pinned = [store.variant(variant_id) or variant_id for variant_id in
                  case_obj.get('suspects', [])]
    variant_obj = store.variant(variant_id)
    clinvar_submission_objs = store.clinvars(submission_id=submission_id)
    return dict(
        today = str(date.today()),
        institute=institute_obj,
        case=case_obj,
        variant=variant_obj,
        pinned_vars=pinned,
        clinvars = clinvar_submission_objs
    )

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

def populate_filters_form(store, institute_obj, case_obj, user_obj,
                          category, request_form):
    # Update filter settings if Clinical Filter was requested
    clinical_filter_panels = []

    default_panels = []
    for panel in case_obj['panels']:
        if panel.get('is_default'):
            default_panels.append(panel['panel_name'])

    # The clinical filter button will only
    if case_obj.get('hpo_clinical_filter'):
        clinical_filter_panels = ['hpo']
    else:
        clinical_filter_panels = default_panels

    FiltersFormClass = VariantFiltersForm
    if category == 'snv':
        FiltersFormClass = FiltersForm
        clinical_filter = MultiDict({
            'variant_type': 'clinical',
            'region_annotations': ['exonic','splicing'],
            'functional_annotations': SEVERE_SO_TERMS,
            'clinsig': [4,5],
            'clinsig_confident_always_returned': True,
            'gnomad_frequency': str(institute_obj['frequency_cutoff']),
            'variant_type': 'clinical',
            'gene_panels': clinical_filter_panels
         })
    elif category == 'sv':
        FiltersFormClass = SvFiltersForm
        clinical_filter = MultiDict({
            'variant_type': 'clinical',
            'region_annotations': ['exonic','splicing'],
            'functional_annotations': SEVERE_SO_TERMS,
            'thousand_genomes_frequency': str(institute_obj['frequency_cutoff']),
            'clingen_ngi': 10,
            'swegen': 10,
            'size': 100,
            'gene_panels': clinical_filter_panels
         })
    elif category == 'cancer':
        FiltersFormClass = CancerFiltersForm
        clinical_filter = MultiDict({
            'variant_type': 'clinical',
            'region_annotations': ['exonic','splicing'],
            'functional_annotations': SEVERE_SO_TERMS,
        })

    if bool(request_form.get('clinical_filter')):
        form = FiltersFormClass(clinical_filter)
# no longer needed?
#            form.csrf_token = request.args.get('csrf_token')
    elif bool(request_form.get('save_filter')):
        # The form should be applied and remain set the page after saving
        form = FiltersFormClass(request_form)
        # Stash the filter to db to make available for this institute
        filter_obj = request_form
        store.stash_filter(filter_obj, institute_obj, case_obj, user_obj, category)
    elif bool(request_form.get('load_filter')):
        filter_id = request_form.get('filters')
        filter_obj = store.retrieve_filter(filter_id)
        form = FiltersFormClass(MultiDict(filter_obj))
    elif bool(request_form.get('delete_filter')):
        filter_id = request_form.get('filters')
        institute_id = institute_obj.get('_id')
        filter_obj = store.delete_filter(filter_id, institute_id, current_user.email)
        form = FiltersFormClass(request_form)
    else:
        form = FiltersFormClass(request_form)

    return form

def verified_excel_file(store, institute_list, temp_excel_dir):
    """Collect all verified variants in a list on institutes and save them to file

    Args:
        store(adapter.MongoAdapter)
        institute_list(list): a list of institute ids
        temp_excel_dir(os.Path): folder where the temp excel files are written to

    Returns:
        written_files(int): the number of files written to temp_excel_dir
    """
    document_lines = []
    written_files = 0
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    LOG.info('Creating verified variant document..')

    for cust in institute_list:
        verif_vars = store.verified(institute_id=cust)
        LOG.info('Found {} verified variants for customer {}'.format(len(verif_vars), cust))

        if not verif_vars:
            continue
        unique_callers = set()
        for var_type, var_callers in CALLERS.items():
            for caller in var_callers:
                unique_callers.add(caller.get('id'))
        cust_verified = export_verified_variants(verif_vars, unique_callers)

        document_name = '.'.join([cust, '_verified_variants', today]) + '.xlsx'
        workbook = Workbook(os.path.join(temp_excel_dir,document_name))
        Report_Sheet = workbook.add_worksheet()

        # Write the column header
        row = 0
        for col,field in enumerate(VERIFIED_VARIANTS_HEADER + list(unique_callers)):
            Report_Sheet.write(row,col,field)

        # Write variant lines, after header (start at line 1)
        for row, line in enumerate(cust_verified,1): # each line becomes a row in the document
            for col, field in enumerate(line): # each field in line becomes a cell
                Report_Sheet.write(row,col,field)
        workbook.close()

        if os.path.exists(os.path.join(temp_excel_dir,document_name)):
            written_files += 1

    return written_files
