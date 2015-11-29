# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request

pileup_bp = Blueprint('pileup', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/pileup/static')


@pileup_bp.route('/pileup')
def viewer():
    """Visualize BAM alignments."""
    bam_files = request.args.getlist('bam')
    bai_files = request.args.getlist('bai')
    samples = request.args.getlist('sample')
    alignments = [{'bam': bam, 'bai': bai, 'sample': sample}
                  for bam, bai, sample in zip(bam_files, bai_files, samples)]

    vcf_file = request.args['vcf']
    position = {
        'contig': request.args['contig'],
        'start': request.args['start'],
        'stop': request.args['stop']
    }

    return render_template('pileup.html', alignments=alignments,
                           vcf_file=vcf_file, position=position)
