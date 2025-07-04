import io
import os
import time

import fastapi
import fastapi.responses
import fastapi.templating
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
    logger.info(f"{context.rid_get()} genai query doc '{bucket}/{doc}' query '{query}' try")

    page_referer = f"/buckets/{bucket}"

    query_ok = ""

    try:
        # get doc reference that should already be uploaded
        genai_files = [file for file in services.gemini.files_list() if file.display_name == doc]

        if not genai_files:
            return fastapi.responses.RedirectResponse(page_referer)

        genai_file = genai_files[0]
        doc_type = genai_file.mime_type

        if query:
            t_start = time.time()
            genai_model = services.gemini.genai_model()
            genai_response = genai_model.generate_content([genai_file, query])
            t_secs = round(time.time() - t_start, 2)

            query_response = genai_response.text
            query_ok = f"gemini query completed in {t_secs}s"
        else:
            query_response = ""

        query_code = 0
    except Exception as e:
        logger.error(f"{context.rid_get()} genai query doc '{doc}' exception '{e}'")
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
                "app_name": "Gemini",
                "app_version": app_version,
                "bucket": bucket,
                "doc": doc,
                "doc_type": doc_type,
                "page_referer": page_referer,
                "query": query,
                "query_code": query_code,
                "query_ok": query_ok,
                "query_prompt": "question",
                "query_response": query_response,
            },
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} genai query doc '{doc}' render exception '{e}'")
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
        _gem_doc = services.gemini.file_upload(name=blob_name, data=blob_bytes, mime_type=gcs_blob.content_type)
    except Exception as e:
        logger.error(f"{context.rid_get()} genai bucket '{bucket_name}' blob '{blob_name}' exception '{e}'")

    redirect_path = request.headers.get("referer")
    response = fastapi.responses.RedirectResponse(redirect_path)

    if "HX-Request" in request.headers:
        response.status_code = 303
        response.headers["HX-Redirect"] = redirect_path

    return response
