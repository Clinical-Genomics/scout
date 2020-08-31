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
If you would like to use a locally built scout container instead of the one from dockerhub, run

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

# Using the generated Ignition file to run Fedora CoreOS

The generated Ignition file
https://eriksjolund.github.io/scout/scout.ign
was generated with [.github/workflows/run_fcct.yaml](.github/workflows/run_fcct.yaml)
from the input file [scout.fcc](./scout.fcc)


References:
https://github.com/coreos/fcct
https://github.com/coreos/fcct/blob/master/docs/specs.md

The Ignition file can be used to run Scout in different ways:

* AWS
* Azure
* DigitalOcean
* Exoscale
* GCP
* libvirt
* QEMU
* VMware
* Vultr
* Run in Live mode from USB stick
* Install from USB stick

Fedora CoreOS documentation:
https://docs.fedoraproject.org/en-US/fedora-coreos/
See for instance __User guides__ -> __Provisioning Machines__

## Run Scout in live mode in RAM memory from a USB stick

Download the Bare metal __ISO__ from

https://getfedora.org/en/coreos/download?tab=metal_virtualized&stream=next

Either stop grub in the early boot phase and append the kernel argument
`ignition.config.url=https://eriksjolund.github.io/scout/scout.ign`

or alternatively embed the ignition file _scout.ign_ into the ISO before writing it to the USB stick

```
wget https://eriksjolund.github.io/scout/scout.ign
cat scout.ign | coreos-installer iso embed file.iso
```

## Run Scout on AWS

Doc:
https://docs.fedoraproject.org/en-US/fedora-coreos/provisioning-aws/

A sketch (untested)

```
wget https://eriksjolund.github.io/scout/scout.ign
aws ec2 run-instances <other options> --image-id <ami> --user-data file://scout.ign
```

## Erase computer and install Scout instead

:warning: this will erase the harddrive of the computer.

In case you want to install to the drive _/dev/sda_
append the kernel arguments

* `coreos.inst.install_dev=/dev/sda`
* `coreos.inst.ignition_url=https://eriksjolund.github.io/scout/scout.ign`


# Add users to Scout

A sketch (untested)

1.
``` 
ssh -i ssh_private_key core@<IPADDRESS OF FEDORA-COREOS-MACHINE>
```

2. 


```
podman exec scout-scout scout load user -i $INSTID -u $NAME -id $ADID -m $USERMAIL $ADMIN
```
or maybe

```
podman exec -ti scout-scout scout load user -i $INSTID -u $NAME -id $ADID -m $USERMAIL $ADMIN
```