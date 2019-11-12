# -*- coding: utf-8 -*-
"""
merge_users.py

Migrate old accounts with user_id as objectId to new accounts with _id as emails.
If a user has another account with the same email, info from the old account is
merged into the proper one.

Collection documents that refer to the old user_id are updated to point to the new
one, including cases, events, acmg, clinvar and clinvar_submissions.

Default operation is by dryrun. Add the --live flag to acutally perform changes.
"""
import logging

import click
import coloredlogs
import yaml
import pymongo

import copy

from pprint import pprint as pp

# Adapter stuff
from scout.adapter.mongo import MongoAdapter
from scout.adapter.client import get_connection
from pymongo.errors import ConnectionFailure

from bson import ObjectId

# General, logging
from scout import __version__

from scout.adapter.utils import check_connection

try:
    from scoutconfig import *
except ImportError:
    pass

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)

@click.command()
@click.option('--loglevel', default='INFO', type=click.Choice(LOG_LEVELS),
              help="Set the level of log output.", show_default=True)
@click.option('-db', '--mongodb', help='Name of mongo database [scout]')
@click.option('-u', '--username')
@click.option('-p', '--password')
@click.option('-a', '--authdb', help='database to use for authentication')
@click.option('-port', '--port', help="Specify on what port to listen for the mongod")
@click.option('-h', '--host', help="Specify the host for the mongo database.")
@click.option('-c', '--config', type=click.Path(exists=True),
              help="Specify the path to a config file with database info.")
@click.option('-L', '--live', is_flag=True, help='live run - use with extreme caution')
@click.version_option(__version__)
@click.pass_context
def merge_users(context, mongodb, username, password, authdb, host, port, loglevel, config, live):
    """scout: manage interactions with a scout instance."""
    coloredlogs.install(level=loglevel)

    LOG.info("Running scout version %s", __version__)
    LOG.debug("Debug logging enabled.")

    mongo_config = {}
    cli_config = {}
    if config:
        LOG.debug("Use config file %s", config)
        with open(config, 'r') as in_handle:
            cli_config = yaml.load(in_handle, Loader=yaml.FullLoader)

    mongo_config['mongodb'] = (mongodb or cli_config.get('mongodb') or 'scout')

    mongo_config['host'] = (host or cli_config.get('host') or 'localhost')
    mongo_config['port'] = (port or cli_config.get('port') or 27017)
    mongo_config['username'] = username or cli_config.get('username')
    mongo_config['password'] = password or cli_config.get('password')
    mongo_config['authdb'] = authdb or cli_config.get('authdb') or mongo_config['mongodb']
    mongo_config['omim_api_key'] = cli_config.get('omim_api_key')


    # always dryrun for now
    dryrun = True
    if live:
        dryrun = False

    LOG.info("Setting database name to %s", mongo_config['mongodb'])
    LOG.debug("Setting host to %s", mongo_config['host'])
    LOG.debug("Setting port to %s", mongo_config['port'])

    valid_connection = check_connection(
        host=mongo_config['host'],
        port=mongo_config['port'],
        username=mongo_config['username'],
        password=mongo_config['password'],
        authdb=mongo_config['authdb'],
    )

    LOG.info("Test if mongod is running")
    if not valid_connection:
        LOG.warning("Connection could not be established")
        context.abort()

    try:
        client = get_connection(**mongo_config)
    except ConnectionFailure:
        context.abort()

    database = client[mongo_config['mongodb']]

    LOG.info("Setting up a mongo adapter")
    mongo_config['client'] = client
    adapter = MongoAdapter(database)

    ## First, create all operation requests that would be needed in a live run.
    user_requests = []
    event_requests = []
    acmg_requests = []
    clinvar_requests = []
    clinvar_submission_requests = []
    case_requests = []

    for oi_user_obj in adapter.user_collection.find({'_id': {'$type':'objectId'}}):
        if not oi_user_obj.get('email'):
            continue

        LOG.info('===USER===')
        oi_user_id = oi_user_obj.get('_id')
        oi_user_email = oi_user_obj.get('email')
        LOG.info("user: {}".format(oi_user_obj))

        create_alt = False
        alt_user_obj = adapter.user_collection.find_one({'_id': oi_user_email})
        if not alt_user_obj:
            create_alt = True
            alt_user_obj = copy.deepcopy(oi_user_obj)
            alt_user_obj['_id'] = oi_user_email
        else:
            LOG.info("alt user: {}".format(alt_user_obj))
            merged_institutes = set()
            merged_institutes.update(alt_user_obj.get('institutes', []) + oi_user_obj.get('institutes', []))
            LOG.info('merged institutes: {}'.format(merged_institutes))
            alt_user_obj['institutes'] = list(merged_institutes)

            merged_roles = set()
            merged_roles.update(alt_user_obj.get('roles', []) + oi_user_obj.get('roles',[]))
            LOG.info('merged roles: {}'.format(merged_roles))
            alt_user_obj['roles'] = list(merged_roles)

            created_at = oi_user_obj.get('created_at')
            alt_created_at = alt_user_obj.get('created_at')
            if ((alt_created_at and created_at) and alt_created_at < created_at):
                created_at = alt_created_at

            if created_at:
                alt_user_obj['created_at'] = created_at

            accessed_at = alt_user_obj.get('accessed_at')
            oi_accessed_at = oi_user_obj.get('accessed_at')
            if (oi_accessed_at and accessed_at) and oi_accessed_at > accessed_at:
                accessed_at = oi_accessed_at

            if accessed_at:
                alt_user_obj['accessed_at'] = accessed_at

        if create_alt:
            LOG.info("create user: {}".format(alt_user_obj))
            operation = pymongo.InsertOne(alt_user_obj)
            user_requests.append(operation)
        else:
            LOG.info("update user: {}".format(alt_user_obj))
            alt_user_id = alt_user_obj.pop('_id')
            operation = pymongo.UpdateOne(
                { '_id': alt_user_id },
                { '$set': alt_user_obj }
            )
            user_requests.append(operation)

        # finally, delete the oi user
        operation = pymongo.DeleteOne(
            {'_id':  ObjectId(str(oi_user_id))}
            )
        user_requests.append(operation)

        ###
        ### events
        ###

        LOG.info('searching for events for user id {}'.format(oi_user_id))
        oi_user_events = adapter.event_collection.find({'user_id': ObjectId(str(oi_user_id))})
        if oi_user_events.count()>0:
            LOG.info('===EVENTS===')
        for event in oi_user_events:
            LOG.info('user event: {}'.format(event))
            event_id = event.get('_id')
            operation = pymongo.UpdateOne(
                {'_id': event_id },
                {
                    '$set': {
                        'user_id': oi_user_email,
                        'user_name': alt_user_obj.get('name')
                        }
                }
            )
            event_requests.append(operation)

        ###
        ### ACMG classifications
        ###
        LOG.info('searching for acmg for user id {}'.format(oi_user_id))
        oi_user_acmg = adapter.acmg_collection.find({'user_id': ObjectId(str(oi_user_id))})
        if oi_user_acmg.count()>0:
            LOG.info('===ACMG===')
            for acmg in oi_user_acmg:
                LOG.info('acmg: {}'.format(acmg))
                operation = pymongo.UpdateOne(
                    {'_id': acmg.get('_id') },
                    {
                        '$set': {
                            'user_id': oi_user_email,
                            'user_name': alt_user_obj.get('name')
                            }
                    }
                )
                acmg_requests.append(operation)

        # Clinvar
        LOG.info('searching for ClinVar for user id {}'.format(oi_user_id))
        oi_user_clinvar = adapter.clinvar_collection.find({'user': ObjectId(str(oi_user_id))})
        if oi_user_clinvar.count()>0:
            LOG.info('=== ClinVar ===')
            for clinvar in oi_user_clinvar:
                LOG.info('acmg: {}'.format(clinvar))
                operation = pymongo.UpdateOne(
                    {'_id': clinvar.get('_id') },
                    {
                        '$set': {
                            'user': oi_user_email,
                            }
                    }
                )
                clinvar_requests.append(operation)

        # clinvar_submission
        LOG.info('searching for clinvar submissions for user id {}'.format(oi_user_id))
        oi_user_clinvars = adapter.clinvar_submission_collection.find({'user_id': ObjectId(str(oi_user_id))})
        if oi_user_clinvars.count()>0:
            LOG.info('=== ClinVar submission ===')
            for clinvars in oi_user_clinvars:
                LOG.info('acmg: {}'.format(clinvars))
                operation = pymongo.UpdateOne(
                    {'_id': clinvars.get('_id') },
                    {
                        '$set': {
                            'user_id': oi_user_email
                            }
                    }
                )
                clinvar_submission_requests.append(operation)

        ###
        ### cases
        ###
        LOG.info('searching for cases assigned to user id {}'.format(oi_user_id))
        oi_user_cases = adapter.case_collection.find({'assignees': ObjectId(str(oi_user_id))})
        if oi_user_cases.count()>0:
            LOG.info('=== Case assignees ===')
            for case in oi_user_cases:
                LOG.info('case {} assignees: {}'.format(case['_id'], case['assignees']))
                operation = pymongo.UpdateOne(
                    {'_id':case.get('_id'), 'assignees': ObjectId(str(oi_user_id))},
                    {
                        '$set': {
                            'assignees.$': oi_user_email
                            }
                    }
                )
                case_requests.append(operation)


    else:
        LOG.info('No ObjectId ID user IDs found - nothing more to do.')



    # if everything worked out ok with dryrun, and after getting this far on a live run,
    # bulk write all proposed changes.
    if event_requests:
        LOG.info('event requests to execute: {}'.format(event_requests))
        if not dryrun:
            result = adapter.event_collection.bulk_write(event_requests, ordered=False)

    if acmg_requests:
        LOG.info('acmg requests to execute: {}'.format(acmg_requests))
        if not dryrun:
            result = adapter.acmg_collection.bulk_write(acmg_requests, ordered=False)
            LOG.info("Modified {} ACMG.".format(result.modified_count))

    if clinvar_requests:
        LOG.info('clinvar requests to execute: {}'.format(clinvar_requests))
        if not dryrun:
            result = adapter.clinvar_collection.bulk_write(clinvar_requests, ordered=False)
            LOG.info("Modified {} ClinVar.".format(result.modified_count))

    if clinvar_submission_requests:
        LOG.info('clinvar sub requests to execute: {}'.format(clinvar_submission_requests))
        if not dryrun:
            result = adapter.clinvar_submission_collection.bulk_write(clinvar_submission_requests, ordered=False)
            LOG.info("Modified {} ClinVar submissions.".format(result.modified_count))

    if case_requests:
        LOG.info('case requests to execute: {}'.format(case_requests))
        if not dryrun:
            result = adapter.case_collection.bulk_write(case_requests, ordered=False)
            LOG.info("Modified {} case submissions.".format(result.modified_count))

    # now delete oi user, and actually update/create alt user
    if user_requests:
        LOG.info('user requests to execute: {}'.format(user_requests))
        if not dryrun:
            result = adapter.user_collection.bulk_write(user_requests, ordered=False)
            LOG.info("Modified users with the following: {}".format(result.bulk_api_result))


if __name__ == '__main__':
    merge_users()
