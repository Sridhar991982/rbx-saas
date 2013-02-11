from __future__ import with_statement
import re
from os.path import basename, isdir, isfile, join, dirname
from shutil import copy
from os import listdir, devnull
from subprocess import check_call
from docutils.core import publish_file
from local_settings import REPO, FILE_EXT, OUTPUT_PREFIX, PDFLATEX, GIT


def run(cmd, cwd=None):
    with open(devnull, 'w') as tempf:
        check_call(cmd, shell=True, stdout=tempf, stderr=tempf, cwd=cwd)


def merge_files(directory):
    merged = join(directory, basename(directory) + FILE_EXT)
    files = listdir(directory)
    files.sort()
    with open(merged, 'w') as outfile:
        for filename in files:
            with open(join(directory, filename)) as infile:
                for line in infile:
                    outfile.write(line)
                outfile.write('\n\n')
    return merged


def copy_assets(template, destination):
    directory = dirname(template)
    if destination != directory:
        for asset in listdir(directory):
            copy(join(directory, asset), destination)


def replace(search, replace, filename):
    run("sed -i ':a;N;$!ba;s/" + search + "/" + replace + "/g' " + filename)


def generate_tex(infile, outfile, template, title, beamer):
    publish_file(source_path=infile,
                 destination_path=outfile,
                 writer_name='latex',
                 settings_overrides={'template': template,
                                     'anchor': False})
    replace('\\\\phantomsection%\\n  \\n', '', outfile)
    replace('\\n\\n}', '}', outfile)
    replace('includegraphics{', 'includegraphics\[width=\\\\linewidth\]{', outfile)
    replace('THETITLE', title, outfile)
    if beamer:
        replace('%\\n  \\\\label{[a-z0-9-]*}%\\n}\\n%*', '}', outfile)
        replace('section{', 'end\{frame\}\\n\\\\begin\{frame\}\{', outfile)


def build_doc(src, template, beamer, request):
    src = REPO + src
    template = REPO + template
    clean()
    pull()
    if isfile(src + FILE_EXT):
        infile = src + FILE_EXT
    elif isdir(src):
        infile = merge_files(src)
    else:
        infile = src
    if not isfile(infile):
        raise Exception('Input file/directory not found')
    if not isfile(template):
        raise Exception('Template does not exists')
    filename = camelcase2separator('.'.join(
                    basename(infile).split('.')[:-1]))
    title = request.GET.get('title', None) or filename.replace('-', ' ').title()
    texfile = join(dirname(infile), OUTPUT_PREFIX + filename + '.tex')
    copy_assets(template, dirname(infile))
    generate_tex(infile, texfile, template, title, beamer)
    compile_tex(texfile)
    return texfile.replace('.tex', '.pdf')


def camelcase2separator(name, separator='-'):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1%s\2' % separator, name)
    return re.sub('([a-z0-9])([A-Z])', r'\1%s\2' % separator, s1).lower()


def compile_tex(texfile):
    # Build twice for ToC
    for i in [1, 2]:
        run(PDFLATEX + ' -bookmarks=true -halt-on-error ' + texfile, dirname(texfile))


def pull():
    run(GIT + ' pull -q', REPO)


def clean():
    #run(GIT + ' clean -qfdx', REPO)
    pass
