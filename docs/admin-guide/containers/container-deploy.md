__Status:__ Experimental. (Don't use for production).

# Deploy Scout using containers

* [ Running Scout using the Dockerfile image ](#docker)
* [ Deploying using Systemd services ](./systemd.md)
* [ Deploying using Kubernetes ](./kubernetes.md)


<a name="docker"></a>
## Scout Dockerfile

A Docker image for creating both backend and frontend containers is available on [Docker Hub](https://hub.docker.com/repository/docker/clinicalgenomics/scout). Alternatively it is possible to build an image starting from the Dockerfile present in this repository.
To build a Scout image on your local computer you need to install [Docker](https://www.docker.com).

To build Scout locally, go to top-level Scout folder (where `Dockerfile` resides) and type:

```
docker build --tag scout .
```

Where `--tag <name>:<tag>` will name and optional tag the Docker Image.

The container with the docker image contains only the app installation files and its required libraries. In order to work, the container must interact with a MongoDB database. This database could be either launched as another Docker image or could run as a mongod instance on your computer or on a remote server.



## Running a Scout web app using a Docker image

Given a MongoDB instance running on localhost, port 27017, the Scout web app could be launched by directly pulling the image from Docker Hub. To launch the demo server run the following command:

```
docker run --net=host --rm --expose 5000 -p 5000:5000 clinicalgenomics/scout scout --host 127.0.0.1 -db scout-demo  serve --host 0.0.0.0
```

From a Mac machine the same command would be slightly different (the reason is described [here](https://docs.docker.com/desktop/mac/networking/)):
```
docker run --platform=linux/amd64 --rm --expose 5000 -p 5000:5000 clinicalgenomics/scout scout --host docker.for.mac.localhost -db scout-demo  serve --host 0.0.0.0
```

### Anatomy of Run Command
The basic structure of the run command is:
```
docker run <image> <command>
```
In our case image is scout. An additional number of arguments are added to open and forward networking ports and for convinience.

* `--rm` will remove the container when it stops executing.
* `--expose` expose port
* `5000:5000` forward port to port on container
* `clinicalgenomics/scout` name of Docker image to run as a container
* `scout --host 127.0.0.1 -db scout-demo  serve --host 0.0.0.0` start Scout with arguments for networking and connecting to database

## Running command line instructions on the fly by running the Docker container

Given a MongoDB instance running on localhost, port 27017, a Scout command line command could be launched in this way:
```
docker run (--net=host) --volume="path_to_config.py_on_your_machine":/home/worker/configs/config.py --rm clinicalgenomics/scout scout --flask-config /home/worker/configs/config.py view cases
```

Note that in the above command we are mapping a specific custom config file present on the local machine to a new file `/home/worker/configs/config.py`, created in the Docker container.

Make sure that the custom config file contains the correct settings to connect to your local database, for instance on a Mac machine, it should contain the following lines:

```
MONGO_HOST = "docker.for.mac.localhost" #127.0.0.1 for non-mac machines
MONGO_DBNAME = "scout-demo"
```

## Opening an interactive terminal to execute command line instructions

To run an interactive terminal to execute the command line, type the following:

```
docker run -it --volume="path_to_config.py_on_your_machine":/home/worker/configs/config.py --rm --entrypoint /bin/sh clinicalgenomics/scout
```


## Docker tips and tricks

### Docker Compose
Docker can simplify the development of Scout as it offers a portable configuration-free environment with all dependancies included. The default `docker-compose.yml` file is designed for demoing and not for development. You can extend the included compose file with your own custom configuration to make it more development friendly. For more information on how to extend docker-compose files see [docker docs](https://docs.docker.com/compose/extends/). The following is an example configuration:

``` yaml
services:
  mongodb:
    volumes:
      - ./volumes/mongodb/data:/data/db  #  make db persistent by storing data on host file system
  scout-web:
    environment:
      FLASK_ENV: development  # set environment variables
  command: scout --host mongodb serve --host 0.0.0.0  # not running on demo db
```

### Miscellaneous Tips

* View all installed images together with onfo and names: `docker image -a`
* View all containers: `docker container ls -a`
* Stop a running image: `docker stop <container name>`
