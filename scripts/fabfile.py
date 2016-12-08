# -*- coding: utf-8 -*-
from fabric.api import run, cd, env
from fabric.utils import puts

env.use_ssh_config = True
APP_NAME = 'scout'


def update():
    with cd("~/git/{}".format(APP_NAME)):
        puts("updating {}...".format(APP_NAME))
        run('git pull')
    puts('restarting server...')
    run("~/miniconda/envs/server/bin/supervisorctl restart {}".format(APP_NAME))
