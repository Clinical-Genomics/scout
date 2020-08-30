# Systemd services of Scout

## Requirements

* podman version >= 2.0.4

## Installation

In the Git repo root directory, run

1. Copy systemd unit files to ~/.config/systemd/user

```
mkdir -p ~/.config/systemd/user
cp systemd/scout-pod.service ~/.config/systemd/user
cp systemd/scout-create-datadir.service ~/.config/systemd/user
cp systemd/scout-mongo.service ~/.config/systemd/user
cp systemd/scout-setup-demo.service ~/.config/systemd/user
cp systemd/scout-scout.service ~/.config/systemd/user
```

2. Optional step
If you would like to use a locally built scout container instead of the one from dockerhub

```
podman build -t scout .
sed -i 's/docker.io\/eriksjolund\/scout:dockerhub/localhost\/scout/g' ~/.config/systemd/user/scout-scout.service
sed -i '/TimeoutStartSec=/d' ~/.config/systemd/user/scout-scout.service
```

3.

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
