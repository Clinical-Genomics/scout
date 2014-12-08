# -*- mode: ruby -*-
# vi: set ft=ruby :

$script = <<SCRIPT

# install compilation dependencies
sudo apt-get update
sudo apt-get install -y build-essential software-properties-common python-software-properties libxslt1-dev libxslt1.1 libxml2-dev libxml2 libssl-dev libffi-dev git tmux

# setup python
sudo add-apt-repository -y ppa:fkrull/deadsnakes

# setup node.js
curl -sL https://deb.nodesource.com/setup | sudo bash -

sudo apt-get install -y python2.7 python-dev python-pip python-virtualenv nodejs mongodb python-dateutil

git clone https://github.com/Clinical-Genomics/scout.git
cd scout
git checkout develop

# install python dependencies
sudo pip install -r requirements/dev.txt

# install node.js dependencies
sudo npm install -g coffee-script gulp
sudo npm install

SCRIPT

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "phusion/ubuntu-14.04-amd64"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.network "forwarded_port", guest: 3000, host: 3000
  config.vm.network "forwarded_port", guest: 27017, host: 27217

  # Simlpe Shell provisioning
  config.vm.provision "shell", inline: $script

  # If true, then any SSH connections made will enable agent forwarding.
  # Default value: false
  # config.ssh.forward_agent = true
end
