import re
from os.path import basename, isdir, isfile, join, dirname
from shutil import copy
from os import listdir
from subprocess import call
from docutils.core import publish_file
from django.http import HttpResponse

TPL_REPORT = 'template/rbx-report.tex'
TPL_ARTICLE = 'template/rbx-article.tex'
TPL_SLIDE = 'template/rbx-slide.tex'
REPO = '%s/../rbx-docs/' % dirname(__file__)


def merge_files(directory):
    if not isdir(directory):
        return directory, False
    merged = join(directory, '%s.md' % basename(directory))
    files = listdir(directory)
    files.sort()
    with open(merged, 'w') as outfile:
        for filename in files:
            with open(join(directory, filename)) as infile:
                for line in infile:
                    outfile.write(line)
                outfile.write('\n\n')
    return merged, True


def copy_assets(template, destination):
    if not isfile(template) or not isdir(destination):
        return False
    directory = dirname(template)
    if destination == directory:
        return True
    try:
        for asset in listdir(directory):
            copy(join(directory, asset), destination)
    except:
        return False
    else:
        return True


def pull_repo():
    call('cd %s && git clean -fdx' % REPO, shell=True)
    call('cd %s && git pull' % REPO, shell=True)


def generate_tex(infile, outfile, template, title, beamer=False):
    with open(infile) as rst, open(outfile, 'w+') as tex:
        tex.write(publish_file(rst, writer_name='latex',
            settings_overrides={
                'template': template,
                'anchor': False,
        }))
    # The ugly part, to be refactored
    if template == REPO + TPL_ARTICLE:
        call("sed -i ':a;N;$!ba;s/\\n\\n}/}/g' %s" % outfile, shell=True)
        call("sed -i 's/section/subsection/' %s" % outfile, shell=True)
        call("sed -i 's/thesubsection/section/' %s" % outfile, shell=True)
    if template == REPO + TPL_REPORT:
        call("sed -i ':a;N;$!ba;s/\\n\\n}/}/g' %s" % outfile, shell=True)
        call("sed -i 's/THETITLE/%s/' %s" % (title, outfile), shell=True)
    if beamer:
        pass


def build_doc(src, template, beamer=False, title=None):
    pull_repo()
    src = REPO + src
    template = REPO + template
    if isfile('%s.rst' % src):
        infile = '%s.rst' % src
    else:
        infile, _ = merge_files(src)
    copy_assets(template, dirname(infile))
    filename = camelcase2separator('.'.join(
                basename(infile).split('.')[:-1]))
    title = title or filename.replace('-', ' ').title()
    texfile = join(dirname(infile), 'rbx-%s.tex' % filename)
    generate_tex(infile, texfile, template, title, beamer)
    compile_tex(texfile)
    return texfile.replace('.tex', '.pdf')


def camelcase2separator(name, separator='-'):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1%s\2' % separator, name)
    return re.sub('([a-z0-9])([A-Z])', r'\1%s\2' % separator, s1).lower()


def compile_tex(texfile):
    for i in [1, 2]:
        call('cd %s && pdflatex -bookmarks=true \
             -halt-on-error %s' % (dirname(texfile), texfile),
             shell=True)


def render_pdf(path):
    if not isfile(path):
        return HttpResponse('PDF generation error. Check syntax!')
    with open(path) as pdf:
        response = HttpResponse(pdf.read(), mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % basename(path)
        return response
