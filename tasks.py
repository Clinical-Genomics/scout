# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from invoke import run, task
from invoke.util import log

from configobj import ConfigObj

from mongoengine import connect
from scout.adapter import MongoAdapter
from scout.models import (User, Whitelist, Institute)
from scout.load import load_scout

@task
def setup(email, name="Paul Anderson"):
    """docstring for setup"""
    db_name = 'variantDatabase'
    adapter = MongoAdapter()
    adapter.connect_to_database(
        database=db_name
    )
    
    adapter.drop_database()
    
    institute_obj = Institute(
        internal_id = 'cust000',
        display_name = 'test-institute',
        sanger_recipients = [email]
    )
    
    adapter.add_institute(institute_obj)
    institute = adapter.institute(institute_id=institute_obj.internal_id)
    Whitelist(email=email).save()
    user = User(
      email=email,
      name=name,
      roles=['admin'],
      institutes=[institute]
    )
    user.save()
    
    for index in [1,2]:
        config = ConfigObj("tests/fixtures/config{}.ini".format(index))
        load_scout(
            adapter=adapter,
            case_file=config['ped'], 
            snv_file=config['load_vcf'], 
            owner=config['owner'], 
            sv_file=config['sv_vcf'], 
            case_type='mip', 
            variant_type='clinical', 
            update=False,
            scout_configs=config
        )

@task
def teardown():
    db_name = 'variantDatabase'
    adapter = MongoAdapter()
    adapter.connect_to_database(
        database=db_name
    )
    adapter.drop_database()
    

@task
def test():
  """test - run the test runner."""
  run('python -m pytest tests/', pty=True)


@task(name='test-all')
def testall():
  """test-all - run tests on every Python version with tox."""
  run('tox')

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
