# -*- coding: utf-8 -*-
import logging
import os.path

from flask import abort, Blueprint, render_template, request, make_response

from .partial import send_file_partial
from scout.server.utils import public_endpoint
from scout.server.extensions import store

pileup_bp = Blueprint('pileup', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/pileup/static')
LOG = logging.getLogger(__name__)


@pileup_bp.route('/remote/static', methods=['OPTIONS', 'GET'])
def remote_static():
    """Stream *large* static files with special requirements."""
    file_path = request.args.get('file')
    print(file_path)

    range_header = request.headers.get('Range', None)
    print(range_header)
    if not range_header and file_path.endswith('.bam'):
        return abort(500)

    new_resp = send_file_partial(file_path)
    print(new_resp)
    return new_resp


@pileup_bp.route('/pileup')
def viewer():
    """Visualize BAM alignments."""
    vcf_file = request.args.get('vcf')
    bam_files = request.args.getlist('bam')
    bai_files = request.args.getlist('bai')
    samples = request.args.getlist('sample')
    alignments = [{'bam': bam, 'bai': bai, 'sample': sample}
                  for bam, bai, sample in zip(bam_files, bai_files, samples)]

    position = {
        'contig': request.args['contig'],
        'start': request.args['start'],
        'stop': request.args['stop']
    }

    return render_template('pileup/pileup.html', alignments=alignments,
                           position=position, vcf_file=vcf_file)


@pileup_bp.route('/<variant_id>/igv.xml')
@public_endpoint
def igv(variant_id):
    """Start IGV browser for a variant."""
    variant_obj = store.variant(variant_id)
    case_obj = store.case(variant_obj['case_id'])

    alignments = []
    for individual in case_obj['individuals']:
        bam_path = individual.get('bam_file')
        if bam_path and os.path.exists(bam_path):
            alignments.append({
                'sample': individual['display_name'],
                'bam': individual['bam_file'],
            })
        else:
            LOG.debug("%s: no bam file found", individual['individual_id'])

    position = {
        'contig': "chr{}".format(variant_obj['chromosome']),
        'start': variant_obj['position'] - 100,
        'stop': variant_obj['position'] + 100,
    }

    hgnc_gene_obj = store.hgnc_gene(variant_obj['genes'][0]['hgnc_id'])
    if hgnc_gene_obj:
        vcf_path = store.get_region_vcf(case_obj, gene_obj=hgnc_gene_obj)
    else:
        vcf_path = None

    return render_template(
        'pileup/igv.xml',
        alignments=alignments,
        position=position,
        vcf_file=vcf_path,
    )
