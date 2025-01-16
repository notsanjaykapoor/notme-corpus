import os
import re

import fastapi
import fastapi.responses
import google.cloud.storage
import sqlmodel

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


@app.get("/buckets/{bucket_name}", response_class=fastapi.responses.HTMLResponse)
def bucket_objects_list(
    request: fastapi.Request,
    bucket_name: str,
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """ """
    logger.info(f"{context.rid_get()} bucket '{bucket_name}' objects")

    try:
        gcs_client = google.cloud.storage.Client()
        blobs_list = gcs_client.list_blobs(bucket_name)

        # iterate once to fetch objects
        blobs_list = [blob for blob in blobs_list]

        # get list of uploaded gemini files
        genai_files = services.gemini.files_list()
        genai_file_names = [file.display_name for file in genai_files]

        query_code = 0
        query_result = f"bucket '{bucket_name}' objects"
    except Exception as e:
        blobs_list = []
        query_code = 400
        query_result = f"exception {e}"
        logger.error(f"{context.rid_get()} bucket '{bucket_name}' objects exception '{e}'")

    try:
        response = templates.TemplateResponse(
            request,
            "buckets/objects/list.html",
            {
                "app_name": "Buckets",
                "app_version": app_version,
                "blobs_list": blobs_list,
                "bucket_name": bucket_name,
                "genai_files": genai_files,
                "genai_file_names": genai_file_names,
                "prompt_text": "search",
                "query_code": query_code,
                "query_result": query_result,
            },
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} buckets '{bucket_name}' objects render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    logger.info(f"{context.rid_get()} bucket '{bucket_name}' objects ok")

    return response


@app.get("/buckets", response_class=fastapi.responses.HTMLResponse)
def buckets_list(
    request: fastapi.Request,
    query: str = "",
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """ """
    if "HX-Request" in request.headers:
        htmx_request = 1
        html_template = "buckets/list_table.html"
    else:
        htmx_request = 0
        html_template = "buckets/list.html"

    logger.info(f"{context.rid_get()} buckets list query '{query}'")

    try:
        gcs_client = google.cloud.storage.Client()
        buckets_list = gcs_client.list_buckets()

        if query:
            buckets_list = [bucket for bucket in buckets_list if re.search(rf"{query}", bucket.name)]
        else: # iterate once
            buckets_list = [bucket for bucket in buckets_list]

        query_code = 0
        query_result = f"query '{query}' returned {len(buckets_list)} results"
    except Exception as e:
        buckets_list = []
        query_code = 400
        query_result = f"exception {e}"
        logger.error(f"{context.rid_get()} buckets list exception '{e}'")

    try:
        response = templates.TemplateResponse(
            request,
            html_template,
            {
                "app_name": "Buckets",
                "app_version": app_version,
                "buckets_list": buckets_list,
                "prompt_text": "search",
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
            },
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} buckets list render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    logger.info(f"{context.rid_get()} buckets list query '{query}' ok")

    if htmx_request == 1:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?query={query}"

    return response