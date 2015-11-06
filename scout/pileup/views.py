# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request

pileup_bp = Blueprint('pileup', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/pileup/static')


@pileup_bp.route('/pileup')
def viewer():
    """Visualize BAM alignments."""
    bam_file = request.args.get('bam')
    return render_template('pileup.html', bam_file=bam_file)
