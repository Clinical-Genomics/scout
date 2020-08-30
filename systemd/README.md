# Systemd services of Scout

## Requirements

* podman version >= 2.0.4

## Installation

In the Git repo root directory, run


```
mkdir -p ~/.config/systemd/user
cp systemd/scout-pod.service ~/.config/systemd/user
cp systemd/scout-create-datadir.service ~/.config/systemd/user
cp systemd/scout-mongo.service ~/.config/systemd/user
cp systemd/scout-setup-demo.service ~/.config/systemd/user

```

Then either build a local scout container

```
podman build -t scout .
cp systemd/scout_from_podman_build/scout-scout.service ~/.config/systemd/user
```

or use a scout container from Dockerhub

```
cp systemd/dockerhub/scout-scout.service ~/.config/systemd/user
``

Then 

```
systemctl --user daemon-reload
systemctl --user enable scout-pod.service
```

## Usage

```
systemctl --user start scout-pod.service
firefox http://localhost:5000
```

To see the status of the services

```
systemctl --user status scout-pod.service scout-create-datadir.service scout-mongo.service scout-setup-demo.service scout-scout.service
```

If you would like the services to start automatically after a reboot of your computer,
run

```
loginctl enable-linger $USER
```
