from __future__ import with_statement

from os.path import dirname, basename, join
from fabric.api import local, run, env, cd
from fabric.operations import put
from fabric.contrib.files import sed, exists
from fabric.contrib.project import rsync_project
from fabric.context_managers import quiet

env.hosts = ['rbx@ssh.alwaysdata.com']
PROJECT_NAME = basename(dirname(__file__))


def deploy(configure=False):
    ''' Deploy app on remote server
    '''
    clean()
    rsync_project('.', exclude=['.git', 'rbx.db', 'fabfile.py', 'Makefile',
                    'requirements.txt', 'settings.py'], delete=True)
    with cd(PROJECT_NAME):
        run('ln -fs /usr/local/alwaysdata/python/django/1.4.1/django/' +
            'contrib/admin/static/admin rbx/static')
        run('ln -fs /home/rbx/rbx-django/rbx/static public')
    is_configured = False
    if not configure and exists(join(PROJECT_NAME, 'settings.py')):
        with quiet():
            is_configured = run('test -z ' +
                '`grep backends.dummy settings.py`').succeeded
    else:
        put('settings.py', PROJECT_NAME)
    if not is_configured:
        setup()
    syncdb()


def setup():
    ''' Configure remote app settings
    '''
    with cd(PROJECT_NAME):
        sed('settings.py', 'DEBUG = True', 'DEBUG = False')
        sed('settings.py', 'default', 'test')
        sed('settings.py', 'prod', 'default')

        sed('settings.py', 'django.db.backends.dummy',
                        'django.db.backends.postgresql_psycopg2')
        run('sed -i.bak -r -e "s/PASSWORD\': \'\'/PASSWORD\':' +
            '\'%s\'/g" settings.py' % env.password, quiet=True)


def syncdb():
    ''' Sync remove app database
    '''
    with cd(PROJECT_NAME):
        run('PYTHONPATH=./lib python manage.py syncdb')


def clean():
    ''' Clean local *.pyc
    '''
    local('find -name "*.pyc" -exec rm {} \;')
