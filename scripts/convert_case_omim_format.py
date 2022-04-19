#!/usr/bin/python
# -*- coding: utf-8 -*-

import click
import pymongo
from pymongo import MongoClient
from tabulate import tabulate

CASES_WITH_DIA = {
    "diagnosis_phenotypes": {"$exists": True, "$ne": []}
}  # MongoDB query to locate cases with any diagnosis

SELECT_FIELDS = {
    "owner": 1,
    "display_name": 1,
    "diagnosis_phenotypes": 1,
}  # select only a few important fields using the query above


@click.command()
@click.option("--db_uri", required=True, help="mongodb://user:password@db_url:db_port/db_name")
@click.option("--test", help="Use this flag to test the function", is_flag=True)
def omim_case_fix_format(db_uri, test):
    try:
        db_name = db_uri.split("/")[-1]  # get database name from connection string
        client = MongoClient(db_uri, test)
        db = client[db_name]
        # test connection
        click.echo("database connection info:{}".format(db))

        cases_with_dia = list(db.case.find(CASES_WITH_DIA, SELECT_FIELDS))
        click.echo(f"Total number of cases with diagnosis:{len(cases_with_dia)}")

        # Display cases with old format of diagnosis (a list of integers)
        cases_with_old_dia = [
            case for case in cases_with_dia if isinstance(case["diagnosis_phenotypes"], int)
        ]
        click.echo(f"Total number of cases with old diagnosis format:{len(cases_with_old_dia)}")

        for i, case in enumerate(cases_with_old_dia):
            click.echo(
                f"\nn:{i}\t{case['owner']}\t{case['display_name']}:{case['diagnosis_phenotypes']}"
            )

    except Exception as err:
        click.echo("Error {}".format(err))


if __name__ == "__main__":
    omim_case_fix_format()
