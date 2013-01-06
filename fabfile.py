from __future__ import with_statement

from os.path import dirname, basename
from fabric.api import local, run, env, cd
from fabric.contrib.files import sed
from fabric.contrib.project import rsync_project
from fabric.context_managers import quiet

env.hosts = ['rbx@ssh.alwaysdata.com']
PROJECT_NAME = basename(dirname(__file__))


def deploy():
    clean()
    rsync_project('.', exclude=['.git', 'rbx.db', 'fabfile.py', 'Makefile',
                    'requirements.txt', 'settings.py'], delete=True)
    with cd(PROJECT_NAME):
        run('ln -fs /usr/local/alwaysdata/python/django/1.4.1/django/' +
            'contrib/admin/static/admin rbx/static')
        run('ln -fs /home/rbx/rbx-django/rbx/static public')
    settings()
    syncdb()


def settings():
    with cd(PROJECT_NAME):
        with quiet():
            is_configured = run('test -n ' +
                '`grep backends.dummy settings.py`').succeeded
        if not is_configured:
            sed('settings.py', 'DEBUG = True', 'DEBUG = False')
            sed('settings.py', 'default', 'test')
            sed('settings.py', 'prod', 'default')

            sed('settings.py', 'django.db.backends.dummy',
                            'django.db.backends.postgresql_psycopg2')
            run('sed -i.bak -r -e "s/PASSWORD\': \'\'/PASSWORD\':' +
                '\'%s\'/g" settings.py' % env.password, quiet=True)


def syncdb():
    with cd(PROJECT_NAME):
        run('PYTHONPATH=./lib python manage.py syncdb')


def clean():
    local('find -name "*.pyc" -exec rm {} \;')
