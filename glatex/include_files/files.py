import requests
import os

def download_file_from_google_drive(id, destination):
    def get_confirm_token(response):
        for key, value in list(response.cookies.items()):
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768
        if bool(os.path.split(destination)[0]):
            if not os.path.exists(os.path.split(destination)[0]):
                os.makedirs(os.path.split(destination)[0])

        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

    URL = "https://docs.google.com/uc"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)


def scan_for_files(fn):
    res = []
    with open(fn, 'r') as fid:
        for ln in fid.readlines():
            if ln.strip().startswith('\\begin{document}'):
                break
            elif ln.strip().startswith('%glatex_include'):
                tokens = ln.split(';;')
                if len(tokens) == 3:
                    res.append((tokens[1].strip(), tokens[2].strip()))
    return res


def check_out_files(fn):
    for gid, local_fn in scan_for_files(fn):
        download_file_from_google_drive(gid, local_fn)
