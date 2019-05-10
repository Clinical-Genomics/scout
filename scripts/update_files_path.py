#!/usr/bin/python
# -*- coding: utf-8 -*-
import click
import pymongo
from pymongo import MongoClient

VCF_FILES = ['vcf_snv', 'vcf_sv', 'vcf_str', 'vcf_cancer', 'vcf_snv_research', 'vcf_sv_research', 'vcf_cancer_research']
INDIVIDUAL_FILES = ['bam_file', 'mt_bam', 'vcf2cytosure']


@click.command()
@click.option('--db_uri', required=True, help='mongodb://user:password@db_url:db_port/db_name')
@click.option('-o','--old_path', required=True, help='/old/path/to/files')
@click.option('-n','--new_path', required=True, help='/new/path/to/files')
@click.option('--test',
              help='Use this flag to test the function',
              is_flag=True
)
@click.option('-d','--discover',
              help='Use this flag to create a list of keys where old path is found',
              is_flag=True
)
def do_replace(db_uri, old_path, new_path, test, discover):
    """ This script replaces a substring of the path to files (delivery_report, vcf files
        and individual bam and vcf2cytosure files) with a new substring provided by the user.
        Useful when cases are moved to a new server"""

    try:
        db_name = db_uri.split('/')[-1] # get database name from connection string
        client = MongoClient(db_uri)
        db = client[db_name]
        # test connection
        click.echo('database connection info:{}'.format(db))

        # get all cases
        case_objs = list(db.case.find())
        n_cases = len(case_objs)
        click.echo('Total number of cases in database:{}'.format(n_cases))

        if discover: # print all keys which contain the old_path
            matching_keys = set()
            for i, case in enumerate(case_objs):
                case_keys = list(level_down(old_path,case))
                unique_keys = list(set(case_keys))
                print('\nn:{}\tcase:{}. Matching keys:{}\n'.format(i+1,case['_id'],unique_keys))
                matching_keys.update(case_keys)

            print(matching_keys)
            return

        """
        for i, case in enumerate(case_objs):
            updates = 0
            set_command = {}
            # fix delivery report path
            d_report = case.get('delivery_report')
            if d_report:
                updates += 1
                set_command['delivery_report'] = d_report.replace(old_path, new_path)

            # fix links to VCF files:
            if case.get('vcf_files'):
                for vcf_type in VCF_FILES:
                    path_to_vcf_type = case['vcf_files'].get(vcf_type)
                    if path_to_vcf_type:
                        updates += 1
                        case['vcf_files'][vcf_type] = path_to_vcf_type.replace(old_path, new_path)
                set_command['vcf_files'] = case['vcf_files']

            # fix path to case individual specific files:
            case_individuals = case.get('individuals')
            for z, ind_obj in enumerate(case_individuals):
                for ind_file in INDIVIDUAL_FILES:
                    ind_file_path = ind_obj.get(ind_file)
                    if ind_file_path:
                        updates += 1
                        ind_obj[ind_file] = ind_file_path.replace(old_path, new_path)
                case['individuals'][z] = ind_obj
            if case_individuals:
                set_command['individuals'] = case['individuals']


            click.echo('fixing case {0}/{1} [{2},{3}] --> update {4} paths'.format(i+1, n_cases, case['owner'], case['display_name'], updates))


            # update case object in database
            if updates and test is False:
                match_condition = {'_id' : case['_id']}
                updated_case = db.case.find_one_and_update(match_condition,
                    {'$set':set_command}, return_document=pymongo.ReturnDocument.AFTER)

                if updated_case:
                    click.echo('---> case updated!')
        """

    except Exception as err:
        click.echo('Error {}'.format(err))


def level_down(substring, dictionary, path=''):
    for key, value in dictionary.items():
        if path:
            newpath = path + '.' +key
        else:
            newpath = key
        try:
            if substring in value:
                yield newpath
                #yield value
            elif isinstance(value, dict):
                for result in level_down(substring, value, newpath):
                    yield result
            elif isinstance(value, list):
                for list_item in value:
                    for result in level_down(substring, list_item, newpath):
                        yield result
        except:
            pass

if __name__ == '__main__':
    do_replace()
