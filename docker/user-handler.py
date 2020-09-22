#!/usr/bin/env python3

import argparse
import os

# import docker

parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description="Helper script to add or remove users from database")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--add", action="store_true", help="Add samples to db")
group.add_argument("--remove", action="store_true", help="Removes samples from db")
parser.add_argument("--name", metavar="NAME", type=str, required=False, help="Name of user to add")
parser.add_argument(
    "--instid",
    metavar="INSTID",
    type=str,
    required=False,
    help="Institute ID for user to be added to",
)
parser.add_argument(
    "--adid", metavar="ADID", type=str, required=False, help="AD ID for user to be added to"
)
parser.add_argument(
    "--usermail",
    metavar="USERMAIL",
    type=str,
    required=False,
    help="Email of user to add or remove",
)
parser.add_argument(
    "--admin",
    metavar="ADMIN",
    type=bool,
    required=False,
    help="Add if user should have admin rights",
)
args = parser.parse_args()

if args.add:
    if args.name and args.usermail and args.instid:
        admin = "--admin" if args.admin else ""
        adid = args.adid if args.adid else ""
        print("Adding user...")
        os.system(
            'docker-compose run --rm -e "INSTID={:}" -e "NAME={:}" -e "ADID={:}" -e "USERMAIL={:}" -e "ADMIN={:}" scout-adduser'.format(
                args.instid, args.name, args.adid, args.usermail, admin
            )
        )
    else:
        print("Both --username, --usermail, --adid and --instid have to be specified, exiting...")


elif args.remove:
    if args.usermail:
        print("Removing user...")
        os.system(
            'docker-compose run --rm -e "USERMAIL={:}" scout-removeuser'.format(args.usermail)
        )
    else:
        print("--usermail have to be specified")
