from .utils import doc_builder, TPL_ARTICLE, TPL_REPORT, TPL_SLIDE


def article(request, fileref):
    return doc_builder(request, fileref, TPL_ARTICLE)


def report(request, fileref):
    return doc_builder(request, fileref, TPL_REPORT)


def slide(request, fileref):
    return doc_builder(request, fileref, TPL_SLIDE)
