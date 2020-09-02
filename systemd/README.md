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

## Run Scout in a VM on an Ubuntu 20.04 host with virt-install

Assume you are logged in as the user __mytest__ 

```
mytest@laptop:~$  cat /etc/issue
Ubuntu 20.04.1 LTS \n \l

mytest@laptop:~$ 
```

Download and decompress
```
mytest@laptop:~$ wget https://eriksjolund.github.io/scout/scout.ign
mytest@laptop:~$ wget https://builds.coreos.fedoraproject.org/prod/streams/next/builds/32.20200824.1.0/x86_64/fedora-coreos-32.20200824.1.0-qemu.x86_64.qcow2.xz
mytest@laptop:~$ unxz fedora-coreos-32.20200824.1.0-qemu.x86_64.qcow2.xz
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
Another way is to list the IP address with the command `virsh net-dhcp-leases default`

```
mytest@laptop:~$ virsh net-dhcp-leases default 
 Expiry Time           MAC address         Protocol   IP address           Hostname   Client ID or DUID
------------------------------------------------------------------------------------------------------------
 2020-09-02 21:57:10   52:54:00:88:3c:a3   ipv4       192.168.122.237/24   -          01:52:54:00:88:3c:a3
```

```
mytest@laptop:~$ curl http://192.168.122.237:5000
<!DOCTYPE html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="shortcut icon" href="/favicon">

	
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
	<link rel="stylesheet" href="/static/bs4_styles.css">
	

	
  
</head>

<body>
	
  
    <nav class="navbar navbar-expand-lg navbar-inverse">
      <div class="container-fluid">
        <a class="navbar-brand" href="/institutes">
          <img src="/public/static/scout-logo.png" width="30" height="30" class="d-inline-block align-top" alt=""><font color="white">Scout</font></a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav mr-auto">
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <span class="fa fa-bars"></span>
              </a>
              <div class="dropdown-menu" aria-labelledby="navbarDropdown">
                <a class="dropdown-item" href="/">Home</a>
                <a class="dropdown-item" href="/genes">Genes</a>
                <a class="dropdown-item" href="/panels">Gene Panels</a>
                <a class="dropdown-item" href="/phenotypes">Phenotypes</a>
                <a class="dropdown-item" href="/diagnoses">Diagnoses</a>
                <a class="dropdown-item" href="/users">Users</a>
                <a class="dropdown-item" href="/overview">Institutes</a>
                <a class="dropdown-item" href="/dashboard">Dashboard</a>
                <div class="dropdown-divider"></div>
                <a class="dropdown-item" href="http://www.clinicalgenomics.se/scout/" target='_blank'>User guide</a>
                <a class="dropdown-item" href="https://github.com/Clinical-Genomics/scout/issues" target='_blank'>Open issues</a>
              </div>
            </li>
            
          </ul>
          <ul class="navbar-nav navbar-right">
            
              
            
          </ul>
        </div>
      </div>
    </nav>

	
  <div class="container-fluid">
    
      
    

  
  
<div class="container">
  <div class="jumbotron mt-3 bg-white">
    <h1 class="display-4">Scout</h1>
    <p class="lead">Analyze VCFs quicker and easier</p>
    <hr class="my-4">
    <p>
      Scout allows you to browse VCFs in a web browser, identify
      compound pairs, and solve cases as a team.
    </p>

    <p>Version <strong>4.20</strong></p>

    
      
        <form action="/login">
          <div class="row">
            <div class="col-8">
              <input type="text" placeholder="email" class="form-control" name="email">
            </div>
            <div class="col-4">
              <button type="submit" class="btn btn-primary form-control text-white">Login</button>
            </div>
          </div>
        </form>
      
    
  </div>
  <main>
    <div class="row justify-content-center align-items-center">
      <div class="col-xs-12 col-sm-4">
        <img class="img-responsive center-block" width="250" src="/public/static/logo-scilifelab.png">
      </div>
      <div class="col-xs-12 col-sm-4">
        <img class="img-responsive center-block" width="125" src="/public/static/swedac.png">
      </div>
      <div class="col-xs-12 col-sm-4">
        <img class="img-responsive center-block" width="250" src="/public/static/logo-karolinska.png">
      </div>
    </div>
  </main>
</div>

  </div>


  <!-- Optional JavaScript -->
  <!-- jQuery first, then Popper.js, then Bootstrap JS -->
  
	<script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
	

	

</body>
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