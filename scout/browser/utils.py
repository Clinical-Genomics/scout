# -*- coding: utf-8 -*-


def build_igv_url(chrom, start, end, vcf_file, bam_files,
                  static_base='/remote/static'):
  """Compose IGV URL to generate the '.jnlp' script."""
  locus = "{chrom}:{start}-{end}".format(chrom=chrom, start=start, end=end)

  # prepend static base URL stub
  static_vcf = "{}/{}".format(static_base, vcf_file)
  static_bams = ["{}/{}".format(static_base, bam) for bam in bam_files]

  # compose the full URL
  broad_url = ("http://www.broadinstitute.org/igv/projects/current/igv.php"
               "?sessionURL={vcf},{','.join(bams)}"
               "&genome=hg19&locus={locus}")\
               .format(vcf=static_vcf, bams=static_bams, locus=locus)

  return broad_url
