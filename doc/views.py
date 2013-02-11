from os.path import basename
from django.http import HttpResponse
from .utils import build_doc, clean


def docbuilder(request, fileref, template, beamer=False):
    try:
        path = build_doc(fileref, template, beamer, request)
        with open(path) as pdf:
            response = HttpResponse(pdf.read(), mimetype='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="%s"' % basename(path)
            clean()
        return response
    except Exception, e:
        clean()
        return HttpResponse('Something wrong happened!<br />%s' % e)
