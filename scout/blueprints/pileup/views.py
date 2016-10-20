# -*- coding: utf-8 -*-
from flask import abort, Blueprint, render_template, request

from .partial import send_file_partial

pileup_bp = Blueprint('pileup', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/pileup/static')


@pileup_bp.route('/remote/static', methods=['OPTIONS', 'GET'])
def remote_static():
    """Stream *large* static files with special requirements."""
    file_path = request.args.get('file')

    range_header = request.headers.get('Range', None)
    if not range_header and file_path.endswith('.bam'):
        return abort(500)

    new_resp = send_file_partial(file_path)
    return new_resp


@pileup_bp.route('/pileup')
def viewer():
    """Visualize BAM alignments."""
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

    return render_template('pileup.html', alignments=alignments,
                           position=position)
