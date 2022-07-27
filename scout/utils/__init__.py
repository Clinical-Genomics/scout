# -*- coding: utf-8 -*-
import logging
LOG = logging.getLogger(__name__)

def call_safe(fun, unknown_var):
     """Call unknown_var using fun, return None if exception is caught.
     Args: unknown_var: Object
           fun: Function
     Returns: Object"""
     try:
         return fun(unknown_var)
     except ValueError:
          print(ValueError)
          return None
     except TypeError as _er:
          LOG.error("TypeError {} {}. {}".format(fun, unknown_var, _er))
          return None
