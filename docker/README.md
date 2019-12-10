# Docker image

The following is an example usage of how you can use the docker image included in the repo to build and interact with Scout. There are of course different ways of interacting, this is just presented as one possible solution, and does not contain all possible usage of Scout.

## Building the image

Clone the latest Scout version from Github:  
```
git clone https://github.com/Clinical-Genomics/scout
```

Scout requires MongoDB to run. Easiest is to use the official MongoDB docker image and define usage in the docker-compose file. The docker compose file handles all the docker images associated with scout, and mounts needed folders. It also contains API-keys and any potential certificate files and config files. An example of the docker-compose file is included.

Before setting up the database, make sure to have the following folders, that will be mounted into the container:

- `database/`    # where the MongoDB data is stored
- `sampledata/`  # from where the data is read  
- `vault/`       # contains the config file and all certificate files
- `panels/`      # contains all panels to be added to Scout


Setup the database and run Scout using the `Makefile`:

```
make build    # Builds all images listed in the Makefile
make setup    # Initializes the database and downloads all data to the db
make run      # Starts the scout application using gunicorn
make stop     # Stops the scout application
```


## Handling users in Scout

Users can be added with the help of the script `user-handler.py`. That script can both add and remove users from the database by starting different docker images.

__Add users:__  
```
python3 user-handler.py --add --name <name> --instid <instid> --usermail <usermail>
```
If user should also be admin the flag `--admin True` should be added. `--name` can in this setup not contain spaces due to docker specific issues. `--adid` can also be added for AD/LDAP authentication against the AD.

__Remove users:__  
```
python3 user-handler.py --remove --usermail <usermail>
```

## Loading data into Scout

Data can be loaded into Scout with the script `case-handler.py`.

__Add cases:__
```
python3 case-handler.py --add --folder <folderpath> --yaml <yamlfile>
```

__Remove cases:__
```
python3 case-handler.py --remove --sampleid <family id> --instid <institute id>
```
