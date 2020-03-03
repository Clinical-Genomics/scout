#!/usr/bin/env python3

import argparse
import os

parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description = "Helper script to add or remove cases from database")
parser.add_argument("--id",   metavar = "ID",  type = str,   required = False,    help = "Panel ID for panel")
parser.add_argument("--instid",     metavar = "INSTID",    type = str,   required = False,    help = "Institute ID for sample to remove")
parser.add_argument("--folder",     metavar = "FOLDER",    type = str,   required = False,    help = "Folder where the sample that should be imported is stored")
parser.add_argument("--panel",       metavar = "PANEL",      type = str,   required = False,    help = "panel file")
args = parser.parse_args()

print("docker-compose run --rm -v {:}:/panels -e \"ID={:}\" -e \"INSTID={:}\" -e \"PANEL={:}\" scout-addpanel".format(os.path.abspath(args.folder), args.panel, args.instid, args.panel))
os.system("docker-compose run --rm -e \"ID={:}\" -e \"INSTID={:}\" -e \"PANEL={:}\" scout-addpanel".format(args.id, args.instid, args.panel))


