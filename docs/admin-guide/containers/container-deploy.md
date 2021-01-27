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
