# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from setuptools import setup, find_packages


setup(
  name='scout',
  version='1.1.0',
  url='https://github.com/Clinical-Genomics/scout',
  description='Scout is a Flask template/bootstrap/boilerplate application.',
  author='Robin Andeer',
  author_email='robin.andeer@gmail.com',
  packages=find_packages(exclude=['tests/', 'scripts/']),
  include_package_data=True,
  zip_safe=False,
  install_requires=[
    'Flask',
    'Flask-Script',
    'path.py',
  ],
  scripts=[
    'scripts/scouttools',
  ],
  # test_suite='tests',
  classifiers=[
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries'
  ]
)
