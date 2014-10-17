# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


class BaseAdapter(object):

  """Base class skeleton for a backend adapter."""

  def __init__(self, app=None):
    super(BaseAdapter, self).__init__()

    if app is not None:
      self.init_app(app)

  def init_app(self, app):
    """Lazy initialize extensions post-instansiation."""
    self.app = app

  def find_all(self):
    """Yields all variants (or the first 100) from the data store.
    Generators are encouraged.

    Yields:
      dict: the next variant (at most 100)

    Examples:

      >>> adapter.find_all()
      [{'id': 1, 'CHROM': '2', ...}, ...]

    """
    raise NotImplementedError

  def find_query(self, query):
      """Yields all variants (or the first 100) from the data store
      that matches the filter criteria in the ``query`` attribute.

      Args:
        query (dict): key-value filters to match the variants against

      Yields:
        dict: the next matching variant (at most 100)

      Examples:

        >>> adapter.find_query({'RS': 'rs78426951'})
        [{'id': 12, 'RS': 'rs78426951', ...}, ...]

      """
      raise NotImplementedError

  def find_many(self, variant_ids):
      """Yields multiple variants matching a list of variant ids.
      Ignores non-matching ids, don't raise exceptions in this case.

      Args:
        variant_ids (list): list of variant ids

      Yields:
        dict: the next matching variant

      Examples:

        >>> adapter.find_many([1, 2, 5])
        [{'id': 1, ...}, {'id': 5, ...}]

      """
      raise NotImplementedError

  def find(self, variant_id):
      """Returns a single variant defined by it's unique id. Returns
      ``None`` if it can't find the requested variant.

      Args:
        variant_id (str): unique variant id

      Returns:
        dict or None: variant from the data store or ``None``

      Examples:

        >>> adapter.find('1')
        {'id': 1, 'CHROM': 'X', ...}

      """
      raise NotImplementedError

  def create(self, variant):
      """Creates a new variant in the database and returns it with
      new unique id.

      Args:
        variant (dict): content to be stored in the data store

      Returns:
        dict: the content + the new unique id

      Examples:

        >>> variant = {'CHROM': 'Y', 'POS': 141293}
        >>> adapter.create(variant)
        {'id': 13, 'CHROM': 'Y', 'POS': 141293}

      """
      raise NotImplementedError

  def update(self, variant):
      """Updates a variant uniquely matching the 'id' value in the
      ``variant`` attribute (used like in ``.find_query``. Should
      return updated attributes that might've changed.

      Args:
        variant (dict): variant object to be updated

      Returns:
        dict: the affected (updated) variant
      """
      raise NotImplementedError

  def delete(self, variant):
      """Removes a variant from the data store based on the 'id' value
      in the ``variant`` attribute.

      Args:
        variant (dict): must contain the unique variant id

      Returns:
        dict: the affected (removed) variant
      """
      raise NotImplementedError
