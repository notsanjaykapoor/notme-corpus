import os
import re

import google.cloud.storage
import google.cloud.storage.bucket

import services.storage.gcs


def bucket_folders(bucket_name: str) -> list[str]:
    """
    Return list of top level folders.

    The storage api doesn't seem to have a straightforward to do this.  It seems like you have to get all blobs and filter them
    to get the top level 'folders'.
    """
    folder_names = set()

    blobs_list = services.storage.gcs.blobs_list(bucket_name=bucket_name, prefix="", delimiter="")

    for blob in blobs_list:
        folder_names.add(blob.name.split("/")[0])

    return sorted(list(folder_names))


def bucket_name() -> str:
    """
    Get bucket uri, parse and return bucket name
    """
    bucket_uri = os.environ.get("APP_BUCKET_URI")

    match = re.match(r"^gs:\/\/(.+)", bucket_uri)

    if not match:
        raise ValueError("invalid uri")

    return match[1]


def buckets_list() -> list[google.cloud.storage.bucket.Bucket]:
    """
    List buckets, these are the top level objects.
    """
    client = google.cloud.storage.Client()
    return [b for b in client.list_buckets()]