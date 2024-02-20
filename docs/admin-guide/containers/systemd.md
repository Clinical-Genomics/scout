# Systemd services of Scout

* [ Introduction ](#intro)
* [ General installation on a Linux distro](#general_installation)
  * [ Fixes for using Fedora CoreOS ](#fedora_coreos)
    * [ Generating the igntion file ](#ignition_file)
    * [ Run fedora CoreOS using the ignition file ](#run_ignition)
  * [ Alternative ways of running Scout ](#alternative_boot)

<a name="intro"></a>
## Requirements

* podman version >= 2.0.4

## Introduction

Scout can be run by installing a few systemd unit files (the text files scout-*.service)
into a Linux user's home directory. The Scout software and Mongodb software will then be run in containers from Dockerhub.

| Systemd service | Description |
| --              | --          |
| [scout-pod.service](https://github.com/Clinical-Genomics/scout/blob/master/containers/systemd/scout-pod.service) | Runs a pod in which the other containers will be running |
| [scout-create-datadir.service](https://github.com/Clinical-Genomics/scout/blob/master/containers/systemd/scout-create-datadir.service) | Creates an empty directory that will be used by Mongodb to store data |
| [scout-mongo.service](https://github.com/Clinical-Genomics/scout/blob/master/containers/systemd/scout-mongo.service) | Runs Mongodb in the container docker.io/library/mongo |
| [scout-setup-demo.service](https://github.com/Clinical-Genomics/scout/blob/master/containers/systemd/scout-setup-demo.service) | Loads the demo data by running the container docker.io/clinicalgenomics/scout:latest  |
| [scout-scout.service](https://github.com/Clinical-Genomics/scout/blob/master/containers/systemd/scout-scout.service) | Serves the Scout webserver by running the container docker.io/clinicalgenomics/scout:latest |


It is also possible to run the Scout systemd services in the same way but on a new Fedora CoreOS computer.

<a name="general_installation"></a>
## Installation into the home directory of a Linux user

In the Git repo root directory, run

1. Copy the systemd unit files located under `scout/containers/systemd` to `~/.config/systemd/user`

```
mkdir -p ~/.config/systemd/user
cp scout/containers/systemd/scout-pod.service ~/.config/systemd/user
cp scout/containers/systemd/scout-create-datadir.service ~/.config/systemd/user
cp scout/containers/systemd/scout-mongo.service ~/.config/systemd/user
cp scout/containers/systemd/scout-setup-demo.service ~/.config/systemd/user
cp scout/containers/systemd/scout-scout.service ~/.config/systemd/user
```

2. __Optional step__ If you would like to use a locally built scout container instead of the one from dockerhub, run

```
sed -i 's/docker.io\/clinicalgenomics\/scout:latest/localhost\/scout/g' ~/.config/systemd/user/scout-setup-demo.service
sed -i 's/docker.io\/clinicalgenomics\/scout:latest/localhost\/scout/g' ~/.config/systemd/user/scout-scout.service
sed -i '/TimeoutStartSec=/d' ~/.config/systemd/user/scout-setup-demo.service
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
If the above command should fail due to permission issues, run it as superuser (sudo).


<a name="fedora_coreos"></a>
# Using Fedora CoreOS

<a name="ignition_file"></a>
## Generating the Ignition file _scout.ign_

To start Fedora CoreOS, the [Ignition file](https://docs.fedoraproject.org/en-US/fedora-coreos/producing-ign/) _scout.ign_ is needed.
It is generated from from the input file `scout/containters/systemd/scout.fcc` with the command

```
podman run --rm -v ./systemd:/input:Z quay.io/coreos/fcct:release --pretty --strict -d /input /input/scout.fcc > ./scout.ign
```

(run from the root directory of the Scout repository)

Before generating _scout.ign_, please edit _scout.fcc_ and replace the ssh public key with your ssh public key.

It is possible to automate the generation of _scout.ign_ with a GitHub Actions workflow so that
it is downloadable from GitHub pages (e.g. https://< username >.github.io/scout/scout.ign)

This GitHub Actions workflow generates such an Ignition file:

```
name: Run Fedora CoreOS Configuration Transpiler
on:
  push:
    branch:
      - master

jobs:
  run_fcct:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - run: |
          mkdir output
      - uses: docker://quay.io/coreos/fcct:release
        with:
          args: --pretty --strict -d ./systemd -o output/scout.ign systemd/scout.fcc
      - uses: actions/upload-artifact@v4
        with:
          name: scout.ign
          path: output/scout.ign
      - name: deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./output
```

References:
* https://github.com/coreos/fcct
* https://github.com/coreos/fcct/blob/master/docs/specs.md

<a name="run_ignition"></a>
# Using the generated Ignition file to run Fedora CoreOS

The Ignition file _scout.ign_ can be used to run Scout in different ways:

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

<a name="alternative_boot"></a>
## Run Scout in live mode in RAM memory from a USB stick

Download the Bare metal __ISO__ from

https://getfedora.org/en/coreos/download?tab=metal_virtualized&stream=next

Either stop grub in the early boot phase and append the kernel argument
`ignition.config.url=https://example.com/scout.ign` (adjust URL)

or alternatively embed the ignition file _scout.ign_ into the ISO before writing it to the USB stick

```
cat scout.ign | coreos-installer iso embed file.iso
```

## Run Scout on AWS

Doc:
https://docs.fedoraproject.org/en-US/fedora-coreos/provisioning-aws/

A sketch (untested)

```
aws ec2 run-instances <other options> --image-id <ami> --user-data file://scout.ign
```

## Run Scout in a VM on an Ubuntu 20.04 host with virt-install

Assume you are logged in as the user __mytest__

```
mytest@laptop:~$  cat /etc/issue
Ubuntu 20.04.1 LTS \n \l

mytest@laptop:~$
```

Download and decompress
```
mytest@laptop:~$ wget https://builds.coreos.fedoraproject.org/prod/streams/next/builds/32.20200901.1.0/x86_64/fedora-coreos-32.20200901.1.0-qemu.x86_64.qcow2.xz
mytest@laptop:~$ unxz fedora-coreos-32.20200901.1.0-qemu.x86_64.qcow2.xz
```

Add the line
```
 /home/mytest/scout.ign rk
```

for Apparmor
```
mytest@laptop:~$ sudo cat /etc/apparmor.d/libvirt/TEMPLATE.qemu
#
# This profile is for the domain whose UUID matches this file.
#

#include <tunables/global>

profile LIBVIRT_TEMPLATE flags=(attach_disconnected) {
  #include <abstractions/libvirt-qemu>
}
mytest@laptop:~$ sudo nano /etc/apparmor.d/libvirt/TEMPLATE.qemu
mytest@laptop:~$ sudo cat /etc/apparmor.d/libvirt/TEMPLATE.qemu
#
# This profile is for the domain whose UUID matches this file.
#

#include <tunables/global>

profile LIBVIRT_TEMPLATE flags=(attach_disconnected) {
  #include <abstractions/libvirt-qemu>
 /home/mytest/scout.ign rk,
}
mytest@laptop:~$
```

```
mytest@laptop:~$ virt-install --connect qemu:///system -n firsttest -r "2048" --os-variant=fedora31 --import --graphics=none --disk "size=15,backing_store=/home/mytest/fedora-coreos-32.20200824.1.0-qemu.x86_64.qcow2"         --qemu-commandline="-fw_cfg name=opt/com.coreos/config,file=/home/mytest/scout.ign"
```
The IP address is printed on the screen the installation.
Another way to list the IP address, is to run the command `virsh net-dhcp-leases default`

```
mytest@laptop:~$ virsh net-dhcp-leases default
 Expiry Time           MAC address         Protocol   IP address           Hostname   Client ID or DUID
------------------------------------------------------------------------------------------------------------
 2020-09-02 21:57:10   52:54:00:88:3c:a3   ipv4       192.168.122.237/24   -          01:52:54:00:88:3c:a3
```

Download the Scout web page

```
mytest@laptop:~$ curl -s http://192.168.122.90:5000 | head -1
<!DOCTYPE html>
mytest@laptop:~$
```

## Erase computer and install Scout instead

:warning: This will erase the harddrive of the computer.

In case you want to install to the drive _/dev/sda_
append the kernel arguments

* `coreos.inst.install_dev=/dev/sda`
* `coreos.inst.ignition_url=https://example.com/scout.ign`


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
