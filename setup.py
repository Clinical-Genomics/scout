# -*- coding: utf-8 -*-

from setuptools import setup

setup(
  name="scout",
  version='0.0.1',
  url='https://github.com/robinandeer/scout',
  description='Scout is a Flask template/bootstrap/boilerplate application.',
  author='Robin Andeer',
  author_email='robin.andeer@gmail.com',
  packages=['scout'],
  include_package_data=True,
  zip_safe=False,
  install_requires=[
    'Flask',
    'Flask-Babel',
    'Flask-Cache',
    'Flask-Script',
    'path.py',
  ],
  test_suite='tests',
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