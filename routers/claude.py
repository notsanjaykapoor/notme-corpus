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
import services.anthropic

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers")

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

app_version = os.environ["APP_VERSION"]


@app.get("/claude/query", response_class=fastapi.responses.HTMLResponse)
def claude_query(
    request: fastapi.Request,
    bucket: str,
    doc: str,
    query: str = "",
):
    """ """
    logger.info(f"{context.rid_get()} claude query doc '{doc}' query '{query}' try")

    page_referer = f"/buckets/{bucket}"

    query_code = 0
    query_error = ""
    query_ok = ""
    query_response = ""

    try:
        # get doc reference that should already be uploaded
        files_list = [file for file in services.anthropic.files_list() if file.filename == doc]

        if not files_list:
            return fastapi.responses.RedirectResponse(page_referer)
        
        anthropic_file = files_list[0]

        if query:
            t_start = time.time()
            anthropic_message = services.anthropic.query_doc(file_id=anthropic_file.id, query=query)
            t_secs = round(time.time() - t_start, 2)

            query_response = anthropic_message.content[0].text
            query_ok = f"anthropic query completed in {t_secs}s"
    except Exception as e:
        logger.error(f"{context.rid_get()} claude query doc '{doc}' exception '{e}'")
        query_code = 500
        query_response = str(e)

    logger.info(f"{context.rid_get()} claude query doc '{doc}' ok")

    if "HX-Request" in request.headers:
        html_template = "claude/query_fragment.html"
    else:
        html_template = "claude/query.html"

    try:
        response = templates.TemplateResponse(
            request,
            html_template,
            {
                "app_name": "Claude",
                "app_version": app_version,
                "bucket": bucket,
                "doc": doc,
                "page_referer": page_referer,
                "query": query,
                "query_code": query_code,
                "query_error": query_error,
                "query_ok": query_ok,
                "query_prompt": "question",
                "query_response": query_response,
            },
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} claude query doc '{doc}' render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    if "HX-Request" in request.headers:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?bucket={bucket}&doc={doc}&query={query}"

    return response


@app.put("/claude/upload", response_class=fastapi.responses.HTMLResponse)
def claude_upload(
    request: fastapi.Request,
    bucket_name: str,
    blob_name: str,
):
    """ """
    logger.info(f"{context.rid_get()} claude bucket '{bucket_name}' blob '{blob_name}' upload")

    try:
        # get blob contents
        # note that blob object here does not include size attribute, so we manually set blob_size below
        gcs_client = google.cloud.storage.Client()
        gcs_bucket = gcs_client.bucket(bucket_name)
        gcs_blob = gcs_bucket.blob(blob_name)
        blob_bytes = io.BytesIO(gcs_blob.download_as_bytes())

        # upload file
        _result = services.anthropic.file_upload(name=blob_name, data=blob_bytes, mime_type=gcs_blob.content_type)

        logger.info(f"{context.rid_get()} claude bucket '{bucket_name}' blob '{blob_name}' upload ok")
    except Exception as e:
        logger.error(f"{context.rid_get()} claude bucket '{bucket_name}' blob '{blob_name}' upload exception '{e}'")
        # claude_file_names = []

    redirect_path = request.headers.get("referer")
    response = fastapi.responses.RedirectResponse(redirect_path)

    if "HX-Request" in request.headers:
        response.status_code = 303
        response.headers["HX-Redirect"] = redirect_path

    return response
