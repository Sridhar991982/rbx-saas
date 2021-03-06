from __future__ import with_statement

from os.path import dirname, basename, join
from fabric.api import local, run, env, cd
from fabric.operations import put
from fabric.contrib.files import sed, exists
from fabric.contrib.project import rsync_project
from fabric.context_managers import quiet

env.hosts = ['rbx@ssh.alwaysdata.com']
PROJECT_NAME = basename(dirname(__file__))
CSS_DIR = 'rbx/static/css'
JS_DIR = 'rbx/static/js'


def deploy(configure=False):
    ''' Deploy app on remote server
    '''
    clean()
    rsync_project('.', exclude=['.git', 'rbx.db', 'fabfile.py', 'Makefile',
                    'requirements.txt', 'settings.py', '.venv', 'rbx-docs'], delete=True)
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
                        'django.db.backends.mysql')
        run('sed -i.bak -r -e "s/PASSWORD\': \'\'/PASSWORD\':' +
            '\'%s\'/g" settings.py' % env.password, quiet=True)


def syncdb():
    ''' Sync remove app database
    '''
    django('syncdb')


def clean():
    ''' Clean local *.pyc
    '''
    local('find -name "*.pyc" -exec rm {} \;')


def _compile_less(name):
    opt = {'dir': CSS_DIR, 'name': name}
    local('recess --compile %(dir)s/%(name)s.less > %(dir)s/%(name)s.css'
            % opt)
    local('recess --compress %(dir)s/%(name)s.css > %(dir)s/%(name)s.min.css'
            % opt)
    local('rm %(dir)s/%(name)s.css' % opt)


def compile():
    _compile_less('rbx')
    _compile_less('bootstrap')
    _compile_less('responsive')
    local('uglifyjs %(dir)s/rbx.js -o %(dir)s/rbx.min.js -c'
            % {'dir': JS_DIR})


def serve():
    django('runserver')


def django(arg):
    local('python manage.py %s' % arg)
