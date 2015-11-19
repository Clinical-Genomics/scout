# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request

pileup_bp = Blueprint('pileup', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/pileup/static')


@pileup_bp.route('/pileup')
def viewer():
    """Visualize BAM alignments."""
    bam_files = request.args.getlist('bam')
    vcf_file = request.args['vcf']
    position = {
        'contig': request.args['contig'],
        'start': request.args['start'],
        'stop': request.args['stop']
    }

    return render_template('pileup.html', bam_files=bam_files,
                           vcf_file=vcf_file, position=position)
