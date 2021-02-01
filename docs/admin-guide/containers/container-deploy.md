__Status:__ Experimental. (Don't use for production).

# Deploy Scout using containers

* [ Scout Dockerfile ](#docker)
* [ Deploying using Systemd services ](./systemd.md)
* [ Deploying using Kubernetes ](./kubernetes.md)


<a name="docker"></a>
## Scout Dockerfile

A Docker image for creating both backend and frontend containers is available on [Docker Hub](https://hub.docker.com/repository/docker/clinicalgenomics/scout). Alternatively the Dockerfile used for creating the image is available in this repository.

A local image of the repository can be created by moving the Dockerfile in the root folder of the app and from the same location, in a terminal, running the following command:

docker build -t scout .

The container with the docker image contains only the app installation files and its required libraries. In order to work, the container must be connected with at least one other container hosting a running mongodb instance or a database running on the local machine.


## Docker tips and tricks

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
