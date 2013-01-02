from django.utils import simplejson
from django.http import HttpResponse


def render_json(pyobj):
    return HttpResponse(simplejson.dumps(pyobj), mimetype='application/json')
