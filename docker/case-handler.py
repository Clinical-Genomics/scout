#!/usr/bin/env python3

import argparse
import os

parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description="Helper script to add or remove cases from database")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--add", action="store_true", help="Add samples to db")
group.add_argument("--remove", action="store_true", help="Removes samples from db")
parser.add_argument(
    "--sampleid",
    metavar="SAMPLEID",
    type=str,
    required=False,
    help="Sample ID for sample to remove (defined under 'family' in yaml file",
)
parser.add_argument(
    "--instid", metavar="INSTID", type=str, required=False, help="Institute ID for sample to remove"
)
parser.add_argument(
    "--folder",
    metavar="FOLDER",
    type=str,
    required=False,
    help="Folder where the sample that should be imported is stored",
)
parser.add_argument(
    "--yaml", metavar="YAML", type=str, required=False, help="yaml file for sample to be imported"
)
args = parser.parse_args()

if args.add:
    if args.folder and args.yaml:
        print("Adding sample...")
        os.system(
            'docker-compose run --rm -v {:}:/sample -e "YAML={:}" scout-import'.format(
                os.path.abspath(args.folder), args.yaml
            )
        )
    else:
        print("Both --folder and --yaml have to be specified, exiting...")


elif args.remove:
    if args.sampleid and args.instid:
        print("Removing sample...")
        os.system(
            'docker-compose run --rm -e "SAMPLEID={:}" -e "INSTID={:}" scout-remove'.format(
                args.sampleid, args.instid
            )
        )
    else:
        print("Both --sampleid and --instid have to be specified")
