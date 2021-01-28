# Example deploying Scout using Kubernetes
Kubernetes is an open-source platform for managing containerized applications. This tutorial will show how to setup a virtual box containing a master and a work node on a local virtual machine using [minikube](https://github.com/kubernetes/minikube) and how to setup the necessary containers to run a MongoDB instance, a pod with the Scout command line and a pod with the Scout server on macOS. Alternatively, for macOS and Windows, consider  [Docker Desktop](https://www.docker.com/products/docker-desktop) which has builtin Kubernetes support. The default install locations for Docker Desktop do overlap with Homebrew hyperkit and minikube so it is easiest to pick one of the alternatives.

### Requirements
1. Install hyperkit and minikube on your local machine (OS X 10.10.3 Yosemite or later):
```
brew install hyperkit
brew install minikube
```
The second command, brew install minikube, will install also the Kubernetes cli (kubectl). Minikube can be alternatively installed using another container manager, such as Podman or VMWare. More documentation is available [here](https://minikube.sigs.k8s.io/docs/start/).

### Installation and Setup of the database and config files
1. Start minikube kubernetes cluster inside hypervisor (hyperkit):
```
minikube start --vm-driver=hyperkit
```
1. Note that all files described in this tutorial are available in the folder "containers", in the scout root directory.

1. The file named "secrets.yaml" contains 2 files: one storing the secrets for the mongodb service (mongodb-secret) and one for the secrets of the Scout app (scout-secret). Secrets can also be stored in different files. In the example they're on the same file, separated by "---".
```
# mongodb secrets
apiVersion: v1
kind: Secret
metadata:
  name: mongodb-secret
type: Opaque
data:
  mongodb-root-username: dXNlcm5hbWU= # base-64 encoded "username"
  mongodb-root-password: cGFzc3dvcmQ= # base-64 encoded "password"
```
1.
```
# scout secrets
apiVersion: v1
kind: Secret
metadata:
  name: scout-secret
type: Opaque
data:
  scout-username: c2NvdXRVc2Vy # base-64 encoded "scoutUser"
  scout-password: c2NvdXRQYXNzd29yZA== # base-64 encoded "scoutPassword"
```
This secret should be edited to include the real scout-username and scout-password. Note that these fields should be base-64 encoded. To encode these strings you can run the following command:
`echo -n "some string" | base64`

1. **Create the above secrets** with the command:
`kubectl apply -f scout/containers/kubernetes/secrets.yaml`

1. Create s ConfigMap for passing setup parameters to Scout pods. This ConfigMap will contain all parameters specified by a python config file. Basic ConfigMap allowing to authenticate to mongodb:
```
apiVersion: v1
kind: ConfigMap
metadata:
  name: scoutconfig
data:
  config.py: |
    MONGO_HOST="mongodb-service"
    MONGO_PORT= 27017
    MONGO_DBNAME= "scout-demo"
    MONGO_USERNAME= "scoutUser"
    MONGO_PASSWORD= "scoutPassword"
```
The config parameters should be modified according to the MongoDB connection settings on the server.

1. **Create the configmap** with the command:
`kubectl apply -f scout/containers/kubernetes/scout-configmap.yaml`

1. Create a Deployment for mongo and a relative service that will run on port 27017. Note that the example file (mongo.yaml) is running a lightweight version image of Mongo (vepo/mongo) and not the official Mongo image. This container can be replaced with any other application that serves a MongoDB using authentication.
Run the Deployment and the service:
`kubectl apply -f scout/containers/kubernetes/mongo.yaml`

### Deploying the Scout command line
To create a running container with the Scout command line can be used a Docker image stored either locally (in that case the Scout Dockerfile should be built first) or on the Docker Hub. This example pulls the latest from Docker Hub to build an interactive pod. Define a scout-cli.yaml file with the following content:
```
# Scout pod for running cli commands
apiVersion: v1
kind: Pod
metadata:
  name: scout-cli
spec:
  containers:
    - name: scout-cli
      image: clinicalgenomics/scout
      tty: true
      volumeMounts:
      - name: config-vol
        mountPath: /config

  volumes:
  - name: config-vol
    configMap:
      name: scoutconfig
```
Note that the configMap representing the config file is mapped inside "volumes". This is necessary to make the content of the config file available to the pod.

1. **Create the pod** with the following command:
`kubectl apply -f scout/containers/kubernetes/scout-cli.yaml`

1. You can launch a shell from this running container using the command:
`kubectl exec -it scout-cli -- bash`

1. From inside the shell, you can run any scout-specific command. For instance to setup the demo database:
`scout --flask-config /config/config.py setup demo`
Note that for connecting to the mongo database it is necessary to provide the param --flask-config with the path to the mapped config file on the container.

### Deploying the Scout server
The scout Deployment file (first file included in the scout-web.yaml example) contains the steps to pull the Scout image from Docker Hub, define a volume with the config file, and launching the server on port 5000:
```
# Deployment document for Scout web server
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scout-web-deployment
  labels:
    app: scout-web
spec:
  replicas: 1
  selector:
    matchLabels:
      app: scout-web
  template:
    metadata:
      labels:
        app: scout-web
    spec:
      volumes:
      - name: config-vol
        configMap:
          name: scoutconfig
      containers:
      - name: scout-web # serve scout pages using scout-web service
        image: clinicalgenomics/scout
        volumeMounts:
        - name: config-vol
          mountPath: /config
        ports:
        - containerPort: 5000
        command: ["scout"]
        args: ["--flask-config", "/config/config.py", "serve", "--host", "0.0.0.0"]
```
The second file present in the configuration represents the service that makes the server available to applications outside the container (for example the web browser):
```
# External service document
apiVersion: v1
kind: Service
metadata:
  name: scout-web-service
spec:
  selector:
    app: scout-web
  type: LoadBalancer
  ports:
    - protocol: TCP
      port: 5000
      targetPort: 5000
      nodePort: 30000
```
1. **create a Scout web server Deployment** with the command:
`kubectl apply -f scout/containers/kubernetes/scout-web.yaml`

### Overview of the running containers and starting the minikube service
1. After the steps above a number of container should be running on the virtual machine. An overview of all containers together with accessory services and itams will be available using the command:
```
kubectl get all
```

1. Start the scout web app service using the command:
```
minikube service scout-web-service
```
This way the app will be accessible in the browser
