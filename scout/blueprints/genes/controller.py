# -*- coding: utf-8 -*-


def gene(record):
    """Parse information about a gene."""
    record['position'] = ("{this[chromosome]}:{this[start]}-{this[end]}"
                          .format(this=record))

    record['inheritance'] = [('AR', record.get('ar')), ('AD', record.get('ad')),
                             ('MT', record.get('mt')), ('XR', record.get('xr')),
                             ('XD', record.get('xd')), ('X', record.get('x')),
                             ('Y', record.get('y'))]
