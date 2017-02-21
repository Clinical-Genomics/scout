# -*- coding: utf-8 -*-


def gene(record):
    """Parse information about a gene."""
    record['position'] = ("{this[chromosome]}:{this[start]}-{this[end]}"
                          .format(this=record))
