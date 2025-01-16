import io
import os

import fastapi
import fastapi.responses
import google.cloud.storage

import context
import log
import main_shared
import services.gemini

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers")

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

app_version = os.environ["APP_VERSION"]


@app.get("/genai/query", response_class=fastapi.responses.HTMLResponse)
def genai_query(
    request: fastapi.Request,
    bucket: str,
    doc: str,
    query: str = "",
):
    """ """
    logger.info(f"{context.rid_get()} genai query doc '{bucket}/{doc}' query '{query}'")

    page_referer = f"/buckets/{bucket}"

    try:
        # get doc reference that should already be uploaded
        genai_files = [file for file in services.gemini.files_list() if file.display_name == doc]

        if not genai_files:
            return fastapi.responses.RedirectResponse(page_referer)

        genai_file = genai_files[0]
        doc_type = genai_file.mime_type

        if query:
            genai_model = services.gemini.genai_model()
            genai_response = genai_model.generate_content([genai_file, query])

            query_response = genai_response.text
        else:
            query_response = ""

        query_code = 0
    except Exception as e:
        logger.error(f"{context.rid_get()} genai query doc '{bucket}/{doc}' exception '{e}'")
        query_code = 500
        query_response = str(e)

    if "HX-Request" in request.headers:
        html_template = "genai/query_fragment.html"
    else:
        html_template = "genai/query.html"

    try:
        response = templates.TemplateResponse(
            request,
            html_template,
            {
                "app_name": "Genai",
                "app_version": app_version,
                "bucket": bucket,
                "doc": doc,
                "doc_type": doc_type,
                "page_referer": page_referer,
                "query": query,
                "query_code": query_code,
                "query_prompt": "question",
                "query_response": query_response,
            },
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} genai query doc '{bucket}/{doc}' render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    logger.info(f"{context.rid_get()} genai query doc '{doc}' ok")

    if "HX-Request" in request.headers:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?bucket={bucket}&doc={doc}&query={query}"

    return response


@app.put("/genai/upload", response_class=fastapi.responses.HTMLResponse)
def genai_upload(
    request: fastapi.Request,
    bucket_name: str,
    blob_name: str,
):
    """ """
    logger.info(f"{context.rid_get()} genai bucket '{bucket_name}' blob '{blob_name}' upload")

    try:
        # get blob contents
        # note that blob object here does not include size attribute, so we manually set blob_size below
        gcs_client = google.cloud.storage.Client()
        gcs_bucket = gcs_client.bucket(bucket_name)
        gcs_blob = gcs_bucket.blob(blob_name)
        blob_bytes = io.BytesIO(gcs_blob.download_as_bytes())

        # upload file
        gem_doc = services.gemini.file_upload(name=blob_name, data=blob_bytes, mime_type=gcs_blob.content_type)

        # get list of uploaded gemini files
        genai_files = [file for file in services.gemini.files_list()]
        genai_file_names = [file.display_name for file in genai_files]
    except Exception as e:
        logger.error(f"{context.rid_get()} genai bucket '{bucket_name}' blob '{blob_name}' exception '{e}'")
        genai_files = []

    try:
        response = templates.TemplateResponse(
            request,
            "buckets/objects/list_table_row.html",
            {
                "blob": gcs_blob,
                "blob_size": gem_doc.size_bytes,
                "bucket_name": bucket_name,
                "genai_files": genai_files,
                "genai_file_names": genai_file_names,
            },
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} genai bucket '{bucket_name}' blob '{blob_name}' render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    logger.info(f"{context.rid_get()} genai bucket '{bucket_name}' blob '{blob_name}' upload ok")

    return response
