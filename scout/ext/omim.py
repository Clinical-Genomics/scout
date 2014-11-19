# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import requests


class OMIM(object):

  """Basic interface to the public OMIM API.

  Can be lazy loaded like other Flask extensions by calling ``init_app``
  post initialization.

  Args:
    app (Flask): Flask instance
    response_format (str): format for response (xml, json, etc.)
  """

  def __init__(self, app=None, response_format='json'):
    super(OMIM, self).__init__()
    self.base_url = 'http://api.europe.omim.org/api'
    self.format = response_format

    if app:
      self.init_app(app)

  def init_app(self, app):
    """Lazy load class after running ``__init__``.

    The Flask config must contain an API key defined as
    ``OMIM_API_KEY``.

    Args:
      app (Flask): initialized Flask app instance
    """
    self.api_key = app.config['OMIM_API_KEY']

  def base(self, handler):
    """Compose url and universal params for any request handler.

    Args:
      handler (str): API entry point

    Returns:
      str, dict: URL entry point and params as a ``dict``
    """
    url = "%s/%s" % (self.base_url, handler)
    params = {
      'apiKey': self.api_key,
      'format': self.format
    }

    return url, params

  def clinical_synopsis(self, mim, include=('clinicalSynopsis',),
                        exclude=None):
    """Get data from ``clinicalSynopsis`` handler.

    Args:
      mim (str): OMIM Phenotype MIM number
      include (list, optional): included sections in response
      exclude (list, optional): exclude sections in response

    Returns:
      response: response object from ``requests``
    """
    url, params = self.base('clinicalSynopsis')
    params['mimNumber'] = mim
    params['include'] = include

    if exclude:
      params['exclude'] = exclude

    return requests.get(url, params=params)

  def entry(self, mim, includes=None, include_all=False):
    """Get data from ``entry`` handler.

    Args:
      mim (str or list): OMIM Phenotype MIM number(s)
      includes (str or list, optional): included sections in response
      include_all (bool, optional): same as ``includes='all'``

    Returns:
      response: response object from ``requests``
    """
    url, params = self.base('entry')

    # add MIM number(s)
    params['mimNumber'] = mim

    # add include section(s)
    if include_all:
      params['include'] = 'all'
    else:
      params['include'] = includes

    # send request
    return requests.get(url, params=params)
