import logging
from scout.utils.md5 import generate_md5_key

LOG = logging.getLogger(__name__)


def load_cytobands(resource, build, adapter):
    """Parse and load cytobands from file.

    Args:
        resource(str): path to cytobands file (either build 37 or 38)
        build(str): "37" or "38"
        adapter(MongoAdapter)

    """
    cytobands = []
    LOG.debug(f"Reading cytoband file for genome build {build}")

    with open(resource) as cytob_file:
        for nline, line in enumerate(cytob_file):
            # Line will look like this:
            # 3	58600000	63800000	p14.2	gneg
            fields = line.split("\t")
            chrom = fields[0]
            band = fields[3]

            cytoband_obj = dict(
                _id=generate_md5_key([build, chrom, band]),
                band=band,
                chrom=str(chrom),  # 3
                start=str(int(fields[1]) + 1),  # 58600000
                stop=str(int(fields[2]) + 1),  # 63800000
                build=str(build),  # "37" or "38"
            )
            cytobands.append(cytoband_obj)

    LOG.debug(f"Found {cytobands} cytobands in the file.")
    adapter.add_cytobands(cytobands)
