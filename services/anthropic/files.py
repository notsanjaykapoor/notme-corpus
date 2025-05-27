import io
import os

import anthropic
import anthropic.types.beta.file_metadata

def file_delete(file_id: str) -> anthropic.types.beta.file_metadata.FileMetadata:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    result = client.beta.files.delete(file_id)

    return result


def file_upload(name: str, data: io.IOBase, mime_type: str) -> anthropic.types.beta.file_metadata.FileMetadata:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    result = client.beta.files.upload(
        file=(name, data, mime_type),
    )

    return result


def files_list() -> list[anthropic.types.beta.FileMetadata]:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return client.beta.files.list()
