# -*- coding: utf-8 -*-
import logging
import os.path

from flask import (abort, Blueprint, render_template, request, current_app, flash)

from .partial import send_file_partial

pileup_bp = Blueprint('pileup', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/pileup/static')


LOG = logging.getLogger(__name__)


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

    genome = current_app.config.get('PILEUP_GENOME')
    if genome:
        if not os.path.isfile(genome):
            flash("The pilup genome path ({}) provided does not exist".format(genome))
            genome = None
    LOG.debug("Use pileup genome %s", genome)

    exons = current_app.config.get('PILEUP_EXONS')
    if exons:
        if not os.path.isfile(exons):
            flash("The pilup exons path ({}) provided does not exist".format(exons))
            genome = None
    LOG.debug("Use pileup exons %s", exons)

    LOG.debug("View alignment for positions Chrom:{0}, Start:{1}, End: {2}".format(
              position['contig'], position['start'], position['stop']))
    LOG.debug("Use alignment files {}".format(alignments))

    return render_template('pileup/pileup.html', alignments=alignments,
                           position=position, vcf_file=vcf_file,
                           genome=genome, exons=exons)
