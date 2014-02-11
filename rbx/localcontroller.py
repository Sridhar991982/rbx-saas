#!/usr/bin/env python
import os
import sys
# If no argument is passed to the script consider we are already in the
# application directory
py_path = os.path.abspath('%s/../' % os.path.abspath(os.path.dirname(__file__)))
if len(sys.argv) == 2:
    py_path = os.path.abspath('%s/../' % sys.argv[1])
if not py_path in sys.path:
    sys.path.append(os.path.abspath('%s/../' % os.path.abspath(os.path.dirname(__file__))))

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from time import sleep
from tempfile import NamedTemporaryFile
from datetime import timedelta, datetime
from settings import VM_POLLING, SITE_URL, VM_SRC
from rbx.models import Run
from subprocess import Popen
from django.template.loader import render_to_string


while True:
    start = datetime.now() + timedelta(seconds=VM_POLLING)
    for run in Run.objects.filter(status__in=[1, 4]):
        state = run.state()
        print('Run #%s, status %s' % (run.pk, state))
        if state in ('failed', 'failure', 'unknown'):
            run.set_status('error')
            print('Error')
        elif run.status == 1 and state == 'running':
            run.set_status('running')
            print('Started')
            with NamedTemporaryFile(delete=False) as temp:
                print(temp.name)
                temp.write(render_to_string('run.sh', {'site_url': SITE_URL,
                                                       'vm_src': VM_SRC,
                                                       'run': run}))
                Popen(['bash', temp.name])
                # os.unlink(temp.name)
        elif run.status == 4:
            print('Running')
            if datetime.now() > (run.started + timedelta(minutes=run.lifetime)):
                run.set_status('aborted')
                print('Aborted')
    sleep((start - datetime.now()).total_seconds())
