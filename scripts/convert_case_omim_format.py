#!/usr/bin/python
# -*- coding: utf-8 -*-

import click
from pymongo import MongoClient

CASES_WITH_DIA = {
    "diagnosis_phenotypes": {"$exists": True, "$ne": []}
}  # MongoDB query to locate cases with any diagnosis

SELECT_FIELDS = {
    "owner": 1,
    "display_name": 1,
    "diagnosis_phenotypes": 1,
}  # select only a few important fields using the query above


@click.command()
@click.option("--db-uri", required=True, help="mongodb://user:password@db_url:db_port")
@click.option("--db-name", required=True, help="db name")
@click.option("--fix", help="Use this flag to fix the OMIM format in old cases", is_flag=True)
def omim_case_fix_format(db_uri, db_name, fix):
    try:
        client = MongoClient(db_uri)
        db = client[db_name]
        # test connection
        click.echo("database connection info:{}".format(db))

        cases_with_dia = list(db.case.find(CASES_WITH_DIA, SELECT_FIELDS))
        click.echo(f"Total number of cases with diagnosis:{len(cases_with_dia)}")

        # Display cases with old format of diagnosis (a list of integers)
        cases_with_old_dia = [
            case for case in cases_with_dia if isinstance(case["diagnosis_phenotypes"][0], int)
        ]
        click.echo(f"Total number of cases with old diagnosis format:{len(cases_with_old_dia)}")

        for i, case in enumerate(cases_with_old_dia):
            click.echo(f"n:{i}\t{case['owner']}\t{case['display_name']}")
            old_dia = case["diagnosis_phenotypes"]
            new_dia = []

            for dia_nr in old_dia:
                disease_term = db.disease_term.find_one({"disease_nr": dia_nr})
                if disease_term is None:
                    click.echo(f"Could not find a disease term with id:{dia_nr}")
                    continue
                new_dia.append(
                    {
                        "disease_nr": dia_nr,
                        "disease_id": disease_term["disease_id"],
                        "description": disease_term["description"],
                    }
                )

            if fix is False:
                new_dia = old_dia
            else:
                db.case.find_one_and_update(
                    {"_id": case["_id"]}, {"$set": {"diagnosis_phenotypes": new_dia}}
                )
            click.echo(f"old dia:{old_dia}--->new dia:{new_dia}\n")

    except Exception as err:
        click.echo("Error {}".format(err))


if __name__ == "__main__":
    omim_case_fix_format()
