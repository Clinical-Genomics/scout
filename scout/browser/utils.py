# -*- coding: utf-8 -*-
from urlparse import urlparse

from flask import abort, flash, request


def build_igv_url(chrom, start, end, vcf_file, bam_files,
                  static_base='remote/static'):
  """Compose IGV URL to generate the '.jnlp' script."""
  locus = "{chrom}:{start}-{end}".format(chrom=chrom, start=start, end=end)

  # prepend static base URL stub
  parsed_uri = urlparse(request.referrer)
  domain = "{uri.scheme}://{uri.netloc}".format(uri=parsed_uri)
  static_vcf = "{}/{}{}".format(domain, static_base, vcf_file)
  static_bams = ["{}/{}{}".format(domain, static_base, bam)
                 for bam in bam_files]

  # check so that all files are set
  if vcf_file is None or len(bam_files) == 0:
    flash("Can't find all required files to launch IGV.")
    return abort(404)

  # compose the full URL
  broad_url = ("http://www.broadinstitute.org/igv/projects/current/igv.php"
               "?sessionURL={vcf},{bams}"
               "&genome=hg19&locus={locus}")\
               .format(vcf=static_vcf, bams=','.join(static_bams), locus=locus)

  return broad_url
