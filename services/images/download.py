import os

import wget

import services.files


def download(uri: str, dir: str) -> str:
    """
    Download uri to specified local dir.  If the uri is already local, skip the download.
    """
    if uri.startswith("file://"):
        _, _, local_path = services.files.file_uri_parse(source_uri=uri)
        return local_path

    os.makedirs(dir, exist_ok=True)

    return wget.download(uri, out=dir)


def download_gc(dir: str) -> str:
    """
    delete files from download directory
    """
