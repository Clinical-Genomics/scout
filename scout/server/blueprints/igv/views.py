# -*- coding: utf-8 -*-
import logging
from flask import (Blueprint, render_template, request, send_file)


igv_bp  = Blueprint('igv', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/igv/static')

LOG = logging.getLogger(__name__)

@igv_bp.route('/igv')
def viewer():
    """Visualize BAM alignments using igv.js (https://github.com/igvteam/igv.js)"""

    locus = 'chr'+request.args['contig']+':'+request.args['start']+'-'+request.args['stop']

    samples = request.args.getlist('sample')
    bam_files = request.args.getlist('bam')
    bai_files = request.args.getlist('bai')

    tracks={}
    sample_tracks = []
    counter = 0
    for sample in samples:
        if bam_files[counter]: # some samples might not have an associated bam file, take care if this
            sample_tracks.append({ 'name' : sample, 'url' : bam_files[counter], 'indexURL' : bai_files[counter] })
        counter += 1

    tracks['sample_tracks'] = sample_tracks
    return render_template('igv_viewer.html', locus=locus, **tracks )


@igv_bp.route('/remote/static', methods=['OPTIONS', 'GET'])
def remote_static():
    """Stream *large* static files with special requirements."""
    file_path = request.args.get('file')

    range_header = request.headers.get('Range', None)
    if not range_header and file_path.endswith('.bam'):
        return abort(500)

    new_resp = send_file(file_path)
    return new_resp
