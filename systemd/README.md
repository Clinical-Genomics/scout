# Systemd services of Scout

## Requirements

* podman version >= 2.0.4

## Installation

In the Git repo root directory, run

```
podman build -t scout .
mkdir -p ~/.config/systemd/user
cp systemd/scout-pod.service ~/.config/systemd/user
cp systemd/scout-create-datadir.service ~/.config/systemd/user
cp systemd/scout-mongo.service ~/.config/systemd/user
cp systemd/scout-setup-demo.service ~/.config/systemd/user
cp systemd/scout-scout.service ~/.config/systemd/user
systemctl --user daemon-reload
systemctl --user enable scout-pod.service
systemctl --user enable scout-create-datadir.service
systemctl --user enable scout-mongo.service
systemctl --user enable scout-setup-demo.service
systemctl --user enable scout-scout.service
```

## Usage

```
systemctl --user start scout-pod.service
firefox http://localhost:5000
```

If you would like the services to start automatically after a reboot of your computer,
run

```
sudo loginctl enable-linger $USER
```
