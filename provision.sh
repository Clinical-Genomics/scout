# install compilation dependencies
sudo apt-get update
sudo apt-get install -y build-essential software-properties-common python-software-properties libxslt1-dev libxslt1.1 libxml2-dev libxml2 libssl-dev libffi-dev git tmux

# setup python
sudo add-apt-repository -y ppa:fkrull/deadsnakes

# setup node.js
curl -sL https://deb.nodesource.com/setup | sudo bash -

# install apt tools
sudo apt-get install -y python2.7 python-dev python-pip python-virtualenv nodejs mongodb python-dateutil

git clone https://github.com/Clinical-Genomics/scout.git
cd scout
git checkout develop

# install python dependencies
sudo pip install -r requirements/dev.txt

# install node.js dependencies
sudo npm install -g coffee-script gulp
sudo npm install
