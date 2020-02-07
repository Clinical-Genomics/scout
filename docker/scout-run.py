#!/usr/bin/env python3

import sys
import os

args = sys.argv.copy()
cmd  = " ".join(args[1:])

# mounts sample folder into container if command is load case
if cmd.startswith('load case'):
    folder = os.path.abspath(os.path.dirname(sys.argv[-1]))
    yaml   = os.path.basename(sys.argv[-1])
    args[-1] = '/sample/'+yaml
else:
    folder = ""

cmd = " ".join(args[1:])
os.system("docker-compose run --rm {:} -e \"CMD={:}\" scout-run".format('-v '+folder+':/sample', cmd))
#os.system("docker-compose run --rm -v {:}:/sample -e \"CMD={:}\" scout-run".format(folder, cmd))
os.system("docker-compose run --rm -e \"CMD={:}\" scout-run".format(cmd))

# add sample
#os.system("docker-compose run --rm -v {:}:/sample -e \"YAML={:}\" scout-import".format(os.path.abspath(args.folder), args.yaml))
# remove sample
#os.system("docker-compose run --rm -e \"SAMPLEID={:}\" -e \"INSTID={:}\" scout-remove".format(args.sampleid, args.instid))

# add user
#os.system("docker-compose run --rm -e \"INSTID={:}\" -e \"NAME={:}\" -e \"ADID={:}\" -e \"USERMAIL={:}\" -e \"ADMIN={:}\" scout-adduser".format(args.instid, args.name, args.adid, args.usermail, admin))

# remove user
#os.system("docker-compose run --rm -e \"USERMAIL={:}\" scout-removeuser".format(args.usermail))
