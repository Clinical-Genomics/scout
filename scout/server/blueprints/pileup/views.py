# -*- coding: utf-8 -*-
from flask import abort, Blueprint, render_template, request, make_response

from .partial import send_file_partial
from scout.server.utils import public_endpoint

pileup_bp = Blueprint('pileup', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/pileup/static')


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


@pileup_bp.route('/igv.xml')
@public_endpoint
def igv():
    """Start IGV browser with a BAM file."""
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

    return render_template('pileup/igv.xml', alignments=alignments,
                           position=position, vcf_file=vcf_file)
