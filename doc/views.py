from django.http import HttpResponse
from .utils import build_doc, render_pdf, TPL_ARTICLE, TPL_REPORT, TPL_SLIDE


def article(request, fileref):
    try:
        title = request.GET.get('title', None)
        pdf = build_doc(fileref, TPL_ARTICLE, title=title)
        return render_pdf(pdf)
    except:
        raise
        return HttpResponse('Something wrong happened!')


def report(request, fileref):
    title = request.GET.get('title', None)
    pdf = build_doc(fileref, TPL_REPORT, title=title)
    return render_pdf(pdf)


def slide(request, fileref):
    title = request.GET.get('title', None)
    pdf = build_doc(fileref, TPL_SLIDE, True, title)
    return render_pdf(pdf)
