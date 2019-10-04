# -*- coding: utf-8 -*-
import logging
import os.path

from flask import (abort, Blueprint, render_template, request, current_app, flash)

from .partial import send_file_partial

alignviewers_bp = Blueprint('alignviewers', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/alignviewers/static')

LOG = logging.getLogger(__name__)


@alignviewers_bp.route('/remote/static', methods=['OPTIONS', 'GET'])
def remote_static():
    """Stream *large* static files with special requirements."""
    file_path = request.args.get('file')

    range_header = request.headers.get('Range', None)
    if not range_header and file_path.endswith('.bam'):
        return abort(500)

    new_resp = send_file_partial(file_path)
    return new_resp

@alignviewers_bp.route('/igv')
def igv():
    """Visualize BAM alignments using igv.js (https://github.com/igvteam/igv.js)"""
    chrom = request.args.get('contig')
    if chrom == 'MT':
        chrom = 'M'

    start = request.args.get('start')
    stop = request.args.get('stop')

    locus = "chr{0}:{1}-{2}".format(chrom,start,stop)
    LOG.debug('Displaying locus %s', locus)

    chromosome_build = request.args.get('build')
    LOG.debug('Chromosome build is %s', chromosome_build)

    samples = request.args.getlist('sample')
    bam_files = request.args.getlist('bam')
    bai_files = request.args.getlist('bai')
    LOG.debug('loading the following tracks: %s', bam_files)

    display_obj={}

    # Add chromosome build info to the track object
    fastaURL = ''
    indexURL = ''
    cytobandURL = ''
    gene_track_format = ''
    gene_track_URL = ''
    gene_track_indexURL = ''

    if chromosome_build == "GRCh38" or chrom == 'M':
        fastaURL = 'https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa'
        indexURL = 'https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa.fai'
        cytobandURL = 'https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg38/cytoBandIdeo.txt'
        gene_track_format = 'gtf'
        gene_track_URL = 'https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg38/genes/Homo_sapiens.GRCh38.80.sorted.gtf.gz'
        gene_track_indexURL = 'https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg38/genes/Homo_sapiens.GRCh38.80.sorted.gtf.gz.tbi'

    else:
        fastaURL = 'https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg19/hg19.fasta'
        indexURL = 'https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg19/hg19.fasta.fai'
        cytobandURL = 'https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg19/cytoBand.txt'
        gene_track_format = 'bed'
        gene_track_URL = 'https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg19/genes/refGene.hg19.bed.gz'
        gene_track_indexURL = 'https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg19/genes/refGene.hg19.bed.gz.tbi'

    display_obj['reference_track'] = {
        'fastaURL' : fastaURL,
        'indexURL' : indexURL,
        'cytobandURL' : cytobandURL
    }

    display_obj['genes_track'] = {
        'name' : 'Genes',
        'type' : 'annotation',
        'format': gene_track_format,
        'sourceType': 'file',
        'url' : gene_track_URL,
        'indexURL' : gene_track_indexURL,
        'displayMode' : 'EXPANDED'
    }

    sample_tracks = []

    counter = 0
    for sample in samples:
        # some samples might not have an associated bam file, take care if this
        if bam_files[counter]:
            sample_tracks.append({ 'name' : sample, 'url' : bam_files[counter],
                                   'indexURL' : bai_files[counter],
                                   'height' : 700
                                   })
        counter += 1

    display_obj['sample_tracks'] = sample_tracks

    if request.args.get('center_guide'):
        display_obj['display_center_guide'] = True
    else:
        display_obj['display_center_guide'] = False

    return render_template('alignviewers/igv_viewer.html', locus=locus, **display_obj )
