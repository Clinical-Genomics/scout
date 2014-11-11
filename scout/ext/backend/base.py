# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


class BaseAdapter(object):

  """Base class skeleton for a backend adapter.

  A fully featured (read-only) adapter should be able to fetch:

  - All cases (VCF files)
  - A single case (including samples metadata)
  - All variants (in a case/VCF)
  - A single variant
  """

  def __init__(self, app=None):
    super(BaseAdapter, self).__init__()

    if app is not None:
      self.init_app(app)

  def init_app(self, app):
    """Lazy initialize extensions post-instansiation."""
    self.app = app

  def cases(self):
    """Fetches all cases from the backend.

    This should include metadata about samples. One case is in most
    cases the same as a single VCF file along with metadata (pedigree.)

    Yields:
      dict: the next case of samples
    """
    raise NotImplementedError

  def case(self, case_id):
    """Fetches a single case based on the unique case ID.

    Args:
      case_id (str): unique case ID

    Returns:
      dict: a single case of samples
    """
    raise NotImplementedError

  def variants(self, query=None, variant_ids=None):
    """Yields all variants (or the first 100) from the data store.

    Generators are encouraged.

    Args:
      query (dict, optional): query object with filter criteria
      variant_ids (list, optional): list of IDs to match against

    Yields:
      dict: the next variant (at most 100)

    Examples:

      >>> adapter.find_query(query={'RS': 'rs78426951'})
        [{'id': 12, 'RS': 'rs78426951', ...}, ...]

    """
    raise NotImplementedError

  def variant(self, variant_id):
      """Returns a single variant defined by it's unique ID. Returns
      ``None`` if it can't find the requested variant.

      Args:
        variant_id (str): unique variant ID

      Returns:
        dict or None: variant from the data store or ``None``

      Examples:

        >>> adapter.find('1')
        {'id': 1, 'CHROM': 'X', ...}

      """
      raise NotImplementedError

  def create_variant(self, variant):
      """Creates a new variant in the database and returns it with
      new unique ID.

      Args:
        variant (dict): content to be stored in the data store

      Returns:
        dict: the content + the new unique ID

      Examples:

        >>> variant = {'CHROM': 'Y', 'POS': 141293}
        >>> adapter.create(variant)
        {'id': 13, 'CHROM': 'Y', 'POS': 141293}

      """
      raise NotImplementedError

  def update_variant(self, variant):
      """Updates a variant uniquely matching the 'id' value in the
      ``variant`` attribute (used like in ``.find_query``. Should
      return updated attributes that might've changed.

      Args:
        variant (dict): variant object to be updated

      Returns:
        dict: the affected (updated) variant
      """
      raise NotImplementedError

  def delete_variant(self, variant):
      """Removes a variant from the data store based on the 'id' value
      in the ``variant`` attribute.

      Args:
        variant (dict): must contain the unique variant id

      Returns:
        dict: the affected (removed) variant
      """
      raise NotImplementedError
