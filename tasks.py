# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from invoke import run, task
from invoke.util import log

from mongoengine import connect
from scout.models import User, Whitelist, Institute


@task
def test():
  """test - run the test runner."""
  run('py.test tests', pty=True)


@task(name='test-all')
def testall():
  """test-all - run tests on every Python version with tox."""
  run('tox')


@task(name='init-data')
def init_data():
  """Bootstrap the database with demo data."""
  # load database with cases, variants, and a default institute
  for case in [21, 22, 23, 31, 32, 33, 34, 51, 53, 54]:
    run("python -m scout.ext.backend.load_mongo "
        "./tests/vcf_examples/%(case)d/variants.vcf "
        "./tests/vcf_examples/%(case)d/%(case)d_pedigree.txt "
        "./configs/config_test.ini -type cmms" % dict(case=case))


@task(name='add-user')
def add_user(email, name='Paul Anderson'):
  """Setup a new user for the database with a default institute."""
  connect('variantDatabase', host='localhost', port=27017)

  institute = Institute.objects.first()
  Whitelist(email=email).save()
  # create a default user
  user = User(
    email=email,
    name=name,
    roles=['admin'],
    institutes=[institute]
  )
  user.save()


@task
def clean():
  """clean - remove build artifacts."""
  run('rm -rf build/')
  run('rm -rf dist/')
  run('rm -rf scout.egg-info')
  run('find . -name __pycache__ -delete')
  run('find . -name *.pyc -delete')
  run('find . -name *.pyo -delete')
  run('find . -name *~ -delete')

  log.info('cleaned up')


@task
def lint():
  """lint - check style with flake8."""
  run('flake8 scout tests')


@task
def coverage():
  """coverage - check code coverage quickly with the default Python."""
  run('coverage run --source scout setup.py test')
  run('coverage report -m')
  run('coverage html')
  run('open htmlcov/index.html')

  log.info('collected test coverage stats')


@task(clean)
def publish(test=False):
  """publish - package and upload a release to the cheeseshop."""
  if test:
    run('python setup.py register -r test sdist upload -r test')
  else:
    run('python setup.py register bdist_wheel upload')
    run('python setup.py register sdist upload')

  log.info('published new release')


@task()
def d(host='0.0.0.0'):
  """Debug."""
  run("python manage.py runserver --host=%s --debug --reload" % host)
