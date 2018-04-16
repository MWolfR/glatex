import os
import subprocess
import shutil
fn_docs = '/home/%s/.config/glatex/documents'
fn_latest = '/home/%s/.config/glatex/latest'
fn_config = '/home/%s/.config/glatex/config.json'


def place_default_config(fn):
    if not os.path.exists(os.path.split(fn)[0]):
        os.makedirs(os.path.split(fn)[0])
    fn_default = os.path.join(os.path.split(__file__)[0], 'config', 'base_config.json')
    import shutil
    print( "No configuration file found at %s. Placing default file. Update contents, if needed!" % fn)
    shutil.copy(fn_default, fn)


def read_config(fn, which_one='default'):
    import json
    with open(fn, 'r') as fid:
        j = json.load(fid)
    config = j[which_one]
    req = ["viewer", "compiler", "doc_extension"]
    for _r in req:
        assert _r in config, "%s not specified by %s/%s" % (_r, fn, which_one)
    return config


def filename_translator(cfg):
    def translate(fn):
        if os.path.exists(fn):
            fn = os.path.abspath(fn)
        for tl in cfg:
            p = tl["parameters"]
            if tl["type"] == "replace_prefix":
                if fn.startswith(p["replace"][0]):
                    fn = p["replace"][1] + fn[len(p["replace"][0]):]
                elif "alternative" in p:
                    fn = p["alternative"] + fn
            elif tl["type"] == "replace":
                fn = fn.replace(p["replace"][0], p["replace"][1])
        return fn
    return translate


def read_docs(fn):
    res = {}
    if os.path.exists(fn):
        with open(fn, 'r') as fid:
            for ln in fid.readlines():
                if len(ln) > 0:
                    splt = ln.strip().split(';;')
                    if len(splt) == 2:
                        res[splt[0]] = (splt[1], os.getcwd())
                    elif len(splt) == 3:
                        res[splt[0]] = (splt[1], splt[2])
                    else:
                        print( "Warning: Skipping line %s" % ln)
    return res


def read_latest():
    latest = read_docs(fn_latest % os.getenv('USER'))
    assert len(latest) > 0, "No recent document found!"
    out_name = latest.keys()[0]
    doc_id = latest[out_name][0]
    out_dir = latest[out_name][1]
    return out_name, doc_id, out_dir


def read_doc_from_file(fn):
    with open(fn, 'r') as fid:
        ln = fid.readline()
        while ln.startswith('#'):
            ln = fid.readline()
        doc_id = ln.strip()
    if len(doc_id) == 0:
        raise Exception("No document id found in %s" % fn)
    out_dir = os.path.split(fn)[0]
    out_name = os.path.split(fn)[1]
    return out_name, doc_id, out_dir


def treat_args(args, append=False, translator=lambda x: x):
    documents = read_docs(fn_docs % os.getenv('USER'))
    if args[0] == 'LATEST':
        latest = read_docs(fn_latest % os.getenv('USER'))
        assert len(latest) > 0, "No recent document found!"
        args[0] = latest.keys()[0]
        documents.update(latest)
    if len(args) == 1:
        if os.path.isfile(translator(args[0])):
            out_name, doc_id, out_dir = read_doc_from_file(translator(args[0]))
        else:
            out_name = args[0]
            assert out_name in documents, ("Unknown doc: %s. Try one of\n%s" % (out_name, str(documents.keys())))
            append = False
            doc_id = documents[out_name][0]
            out_dir = documents[out_name][1]
    else:
        out_dir, out_name = os.path.split(translator(args[1]))
        if len(out_dir) == 0:
            out_dir = os.getcwd()
        doc_id = args[0]
        if doc_id in documents:
            doc_id = documents[doc_id][0]
    out_name = os.path.splitext(out_name)[0]
    if append:
        if os.path.isfile(fn_docs % os.getenv('USER')):
            write_docs(fn_docs % os.getenv('USER'), out_name, doc_id, out_dir, mode='r+')
        else:
            write_docs(fn_docs % os.getenv('USER'), out_name, doc_id, out_dir, mode='w')
    return out_name, doc_id, out_dir


def get_config(profile):
    fn = fn_config % os.getenv('USER')
    if not os.path.exists(fn):
        place_default_config(fn)
    cfg = read_config(fn, which_one=profile)
    return cfg


def write_docs(fn, out_name, doc_id, out_dir, mode='r+'):
    if not os.path.exists(os.path.split(fn)[0]):
        os.makedirs(os.path.split(fn)[0])
    with open(fn, mode) as fid:
        fid.seek(0, 2)
        fid.write('%s;;%s;;%s\n' % (out_name, doc_id, out_dir))


def write_latest(out_name, doc_id, out_dir):
    fn = fn_latest % os.getenv('USER')
    write_docs(fn, out_name, doc_id, out_dir, mode='w')


def configure(argv):
    do_translate_input = True
    profile = 'default'
    args = []
    kwargs = {'do_refresh': True,
              'do_open': True,
              'append': False,
              'make_button': True}
    for arg in argv:
        if arg == '--no-refresh':
            kwargs['do_refresh'] = False
        elif arg == '--no-open':
            kwargs['do_open'] = False
        elif arg == '--no-translate':
            do_translate_input = False
        elif arg == '--append':
            kwargs['append'] = True
        elif arg == '--no-button':
            kwargs['make_button'] = False
        elif arg.startswith('--profile='):
            profile = arg[10:]
        else:
            args.append(arg)
    assert len(args) > 0, "No input specified!"
    config = get_config(profile)
    tl0 = lambda x: x
    if do_translate_input:
        tl0 = filename_translator(config.get("input_translator", []))
    tl1 = filename_translator(config.get("compiler_translator", []))
    tl2 = filename_translator(config.get("viewer_translator", []))
    return config, (tl0, tl1, tl2), args, kwargs


def main(out_name, doc_id, out_dir, config, translators,
         do_refresh=True, do_open=True, make_button=True):
    gdoc_pat = 'https://docs.google.com/document/export?format=txt&id=%s'
    sed_command = r'1 s/\xEF\xBB\xBF//'

    tl1, tl2 = translators
    os.chdir('/tmp')
    pdf_name = out_name + config['doc_extension']
    tex_name = out_name + '.tex'
    if do_refresh:
        subprocess.call(["wget", "-O", tex_name, gdoc_pat % doc_id])
        subprocess.call(["sed", "-i", "-e", sed_command, tex_name])
        compile = [config["compiler"]["exe"]] + config["compiler"].get("args", []) + [tl1(tex_name)]
        subprocess.call(compile)
        shutil.copy(pdf_name, out_dir)
    os.chdir(out_dir)
    if do_open:
        from .recompile_button import Recompiler
        view = [config["viewer"]["exe"]] + config["viewer"].get("args", []) + [tl2(pdf_name)]
        proc = subprocess.Popen(view)
        if make_button:
            button = Recompiler(config, translators)
        proc.wait()
