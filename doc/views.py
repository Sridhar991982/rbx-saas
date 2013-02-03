from django.http import HttpResponse
from .utils import build_doc, render_pdf, TPL_ARTICLE, TPL_REPORT, TPL_SLIDE


def article(request, fileref):
    try:
        pdf = build_doc(fileref, TPL_ARTICLE, request)
        return render_pdf(pdf)
    except:
        return HttpResponse('Something wrong happened!')


def report(request, fileref):
    try:
        pdf = build_doc(fileref, TPL_REPORT, request)
        return render_pdf(pdf)
    except:
        return HttpResponse('Something wrong happened!')


def slide(request, fileref):
    try:
        pdf = build_doc(fileref, TPL_SLIDE, request)
        return render_pdf(pdf)
    except:
        return HttpResponse('Something wrong happened!')
