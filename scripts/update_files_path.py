#!/usr/bin/python
# -*- coding: utf-8 -*-
import click
import pymongo
from pymongo import MongoClient
from tabulate import tabulate

from scout.constants import FILE_TYPE_MAP

VCF_FILES = FILE_TYPE_MAP.keys()
INDIVIDUAL_FILES = ["bam_file", "mt_bam", "vcf2cytosure"]


@click.command()
@click.option("--db_uri", required=True, help="mongodb://user:password@db_url:db_port/db_name")
@click.option("-o", "--old_path", required=True, help="/old/path/to/files")
@click.option("-n", "--new_path", required=True, help="/new/path/to/files")
@click.option("--test", help="Use this flag to test the function", is_flag=True)
@click.option(
    "-d",
    "--discover",
    help="Use this flag to create a list of keys where old path is found",
    is_flag=True,
)
@click.option("-c", "--case_id", help="id of a case that needs fixing")
def do_replace(db_uri, old_path, new_path, test, discover, case_id):
    """This script replaces a substring of the path to files (delivery_report, vcf files
    and individual bam and vcf2cytosure files) with a new substring provided by the user.
    Useful when cases are moved to a new server"""

    try:
        db_name = db_uri.split("/")[-1]  # get database name from connection string
        client = MongoClient(db_uri)
        db = client[db_name]
        # test connection
        click.echo("database connection info:{}".format(db))

        query = {}
        if case_id:
            query["_id"] = case_id
        # get all cases
        case_objs = list(db.case.find(query))
        n_cases = len(case_objs)
        click.echo("Total number of cases in database:{}".format(n_cases))

        if discover:  # print all keys which contain the old_path and should be updated, then exit
            matching_keys = set()
            for i, case in enumerate(case_objs):
                case_keys = list(level_down(old_path, case))
                unique_keys = list(set(case_keys))
                click.echo(
                    "\nn:{}\tcase:{}. Matching keys:{}".format(i + 1, case["_id"], unique_keys)
                )
                matching_keys.update(case_keys)

            click.echo("Unique paths to be updated:{}".format(matching_keys))
            return

        for i, case in enumerate(case_objs):
            fields = []
            replace_fields = []

            set_command = {}
            # fix delivery report path
            d_report = case.get("delivery_report")
            if d_report and old_path in d_report:
                replace_fields.append(["case[delivery_report]", d_report])
                set_command["delivery_report"] = d_report.replace(old_path, new_path)
            elif d_report:
                fields.append(["case[delivery_report]", d_report])

            # fix delivery report when there are analysis-specific reports
            analyses = case.get("analyses")
            update = False
            if analyses:
                for n, analysis in enumerate(analyses):
                    d_report = analysis.get("delivery_report")
                    if d_report and old_path in d_report:
                        replace_fields.append(
                            ["case[analyses][{}][delivery_report]".format(n), d_report]
                        )
                        analyses[n]["delivery_report"] = d_report.replace(old_path, new_path)
                        update = True
                    elif d_report:
                        fields.append(["case[analyses][{}][delivery_report]".format(n), d_report])

            if update:
                set_command["analyses"] = analyses

            # fix delivery report path when 'delivery_path' key exists in case object:
            d_path = case.get("delivery_path")
            if d_path and old_path in d_path:
                replace_fields.append(["case[delivery_path]", d_path])
                set_command["delivery_path"] = d_path.replace(old_path, new_path)
            elif d_path:
                fields.append(["case[delivery_path]", d_path])

            # fix links to VCF files:
            update = False
            if case.get("vcf_files"):
                for vcf_type in VCF_FILES:
                    path_to_vcf_type = case["vcf_files"].get(vcf_type)
                    if path_to_vcf_type and old_path in path_to_vcf_type:
                        replace_fields.append(
                            ["case[vcf_files][{}]".format(vcf_type), path_to_vcf_type]
                        )
                        case["vcf_files"][vcf_type] = path_to_vcf_type.replace(old_path, new_path)
                        update = True
                    elif path_to_vcf_type:
                        fields.append(["case[vcf_files][{}]".format(vcf_type), path_to_vcf_type])
            if update:
                set_command["vcf_files"] = case["vcf_files"]

            # fix path to case individual specific files:
            case_individuals = case.get("individuals")
            update = False
            if case_individuals:
                for z, ind_obj in enumerate(case_individuals):
                    for ind_file in INDIVIDUAL_FILES:
                        ind_file_path = ind_obj.get(ind_file)
                        if ind_file_path and old_path in ind_file_path:
                            update = True
                            ind_obj[ind_file] = ind_file_path.replace(old_path, new_path)
                            replace_fields.append(
                                [
                                    "case[individuals][{}][{}]".format(z, ind_file),
                                    ind_file_path,
                                ]
                            )
                        elif ind_file_path:
                            fields.append(
                                [
                                    "case[individuals][{}][{}]".format(z, ind_file),
                                    ind_file_path,
                                ]
                            )

                    case["individuals"][z] = ind_obj
            if update:
                set_command["individuals"] = case["individuals"]

            click.echo(
                "####### fixing case {0}/{1} [{2},{3}] ########".format(
                    i + 1, n_cases, case["owner"], case["display_name"]
                )
            )

            click.echo("Replace n={} fields with new path.".format(len(replace_fields)))
            print(tabulate(replace_fields, ["key", "path"], tablefmt="grid"))

            # update case object in database
            if replace_fields and test is False:
                match_condition = {"_id": case["_id"]}
                updated_case = db.case.find_one_and_update(
                    match_condition,
                    {"$set": set_command},
                    return_document=pymongo.ReturnDocument.AFTER,
                )

                if updated_case:
                    click.echo("---> case updated!")

            click.echo("other paths:")
            for field in fields:
                print(field)

            click.echo("#" * 100 + "\n\n")

    except Exception as err:
        click.echo("Error {}".format(err))


def level_down(substring, dictionary, path=""):
    for key, value in dictionary.items():
        if path:
            newpath = path + "." + key
        else:
            newpath = key
        try:
            if substring in value:
                yield newpath
                # yield value
            elif isinstance(value, dict):
                for result in level_down(substring, value, newpath):
                    yield result
            elif isinstance(value, list):
                for list_item in value:
                    for result in level_down(substring, list_item, newpath):
                        yield result
        except:
            pass


if __name__ == "__main__":
    do_replace()
