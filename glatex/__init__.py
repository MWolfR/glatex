import os
fn_docs = '/home/%s/.config/glatex/documents'
fn_latest = '/home/%s/.config/glatex/latest'
fn_config = '/home/%s/.config/glatex/config.json'


def place_default_config(fn):
    if not os.path.exists(os.path.split(fn)[0]):
        os.makedirs(os.path.split(fn)[0])
    fn_default = os.path.join(os.path.split(__file__)[0], 'config', 'base_config.json')
    import shutil
    print "No configuration file found at %s. Placing default file. Update contents, if needed!"
    shutil.copy(fn_default, fn)


def read_config(fn, which_one='default'):
    import json
    with open(fn, 'r') as fid:
        j = json.load(fid)
    config = j[which_one]
    req = ["viewer", "compiler", "compiler_translator",
           "viewer_translator", "doc_extension"]
    for _r in req:
        assert _r in config, "%s not specified by %s/%s" % (_r, fn, which_one)
    return config


def filename_translator(cfg):
    def translate(fn):
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
                        print "Warning: Skipping line %s" % ln
    return res


def treat_args(args, append=False):
    documents = read_docs(fn_docs % os.getenv('USER'))
    if args[0] == 'LATEST':
        latest = read_docs(fn_latest % os.getenv('USER'))
        assert len(latest) > 0, "No recent document found!"
        args[0] = latest.keys()[0]
        documents.update(latest)
    if len(args) == 1:
        out_name = args[0]
        assert out_name in documents, ("Unknown doc: %s. Try one of\n%s" % (out_name, str(documents.keys())))
        doc_id = documents[out_name][0]
        out_dir = documents[out_name][1]
        if not out_name.endswith('.tex'):
            out_name = out_name + '.tex'
    else:
        out_dir, out_name = os.path.split(args[1])
        if len(out_dir) == 0:
            out_dir = os.getcwd()
        doc_id = args[0]
        if doc_id in documents:
            doc_id = documents[doc_id][0]
        if not out_name.endswith('.tex'):
            out_name = out_name + '.tex'
        if append:
            write_docs(fn_docs % os.getenv('USER'), out_name, doc_id, out_dir, mode='r+')
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
