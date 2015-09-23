# run this after the ansible provisioning
echo "source activate prod" >> "${HOME}/.bashrc"
source /home/vagrant/miniconda/bin/activate prod
scouttools wipe_and_load
gulp --gulpfile /vagrant/Gulpfile.js build

python /vagrant/manage.py -c /home/vagrant/demo.cfg vagrant &
