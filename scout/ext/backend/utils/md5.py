#!/usr/bin/env python
# encoding: utf-8
"""
generate_md5_key.py

Generate md5-key from a list

Created by Måns Magnusson on 2014-11-10.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""

from __future__ import (absolute_import, print_function,)

import sys
import os
import hashlib
from six import string_types

import click

def generate_md5_key(list_of_arguments):
  """
  Generate an md5-key from a list of arguments.

  Args:
    list_of_arguments: A list of strings

  Returns:
    A md5-key object generated from the list of strings.
  """
  
  for arg in list_of_arguments:
    if not isinstance(arg, string_types):
      raise SyntaxError("Error in generate_md5_key:" \
                        "Argument: {0} is a {1}".format(arg, type(arg)))

  h = hashlib.md5()
  h.update(' '.join(list_of_arguments))

  return h.hexdigest()

@click.command()
@click.option('-v', '--verbose',
                is_flag=True,
                help='Increase output verbosity.'
)
def cli(verbose):
  """
  Test generating md5 key.
  """
  arguments = ['hej', 'du']
  print('Creating md5 key with: %s' % arguments)
  print(generate_md5_key(arguments))

if __name__ == '__main__':
    cli()
