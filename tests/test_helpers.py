# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from scout.helpers import md5ify


def test_md5ify():
  """Test making MD5 key from a list of strings."""
  md5 = md5ify(['Paul', 'Thomas', 'Andersson'])
  assert md5 == 'd0089628bb73a9cbf2a7fbe657eae062'

  assert md5ify('1 2 3 4 5'.split()) == '9f56c817b9cbf8e0a78facd2684b8c55'
