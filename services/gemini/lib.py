import io
import os

import google.generativeai
import google.generativeai.types.file_types


def file_upload(name: str, data: io.IOBase, mime_type: str) -> google.generativeai.types.file_types.File:
    _genai_configure()

    return google.generativeai.upload_file(display_name=name, path=data, mime_type=mime_type)


def files_list():
    _genai_configure()

    # iterate once to get objects
    return [file for file in google.generativeai.list_files()]


def genai_model():
    _genai_configure()
    return google.generativeai.GenerativeModel(os.environ.get("GOOGLE_GEMINI_MODEL"))


def _genai_configure():
    google.generativeai.configure(api_key=os.environ.get("GOOGLE_GEMINI_KEY"))
