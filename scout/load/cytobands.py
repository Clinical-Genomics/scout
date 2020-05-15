import logging

LOG = logging.getLogger(__name__)


def load_cytobands(resource, build, adapter):
    """Parse and load cytobands from file.

    Args:
        resource(str): path to cytobands file (either build 37 or 38)
        build(str): "37" or "38"
        adapter(MongoAdapter)

    """
    cytobands = []
    for line in open(resource):
        # Line will look like this:
        # 3	58600000	63800000	p14.2	gneg
        fields = line.split("\t")
        chrom = fields[0]
        band = fields[3]

        cytoband_obj = dict(
            _id="_".join([chrom, band, build]),  # 3_p14.2
            chrom=chrom,  # 3
            start=fields[1],  # 58600000
            stop=fields[2],  # 63800000
            build=build,  # "37" or "38"
        )
        cytobands.append(cytoband_obj)

    LOG.info(cytobands)
    adapter.add_cytobands(cytobands)
