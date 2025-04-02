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
import services.storage.gcs

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
):
    """ """
    logger.info(f"{context.rid_get()} bucket '{bucket_name}' objects")

    try:
        gcs_client = google.cloud.storage.Client()
        blobs_list = gcs_client.list_blobs(bucket_name)

        # iterate once to fetch objects, and filter
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
                "app_name": "Bucket Blobs",
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
):
    """ """
    logger.info(f"{context.rid_get()} buckets list")

    bucket_name = services.storage.gcs.bucket_name()

    # redirect to single and only bucket
    return fastapi.responses.RedirectResponse(f"/buckets/{bucket_name}")

    try:
        gcs_client = google.cloud.storage.Client()
        buckets_list = gcs_client.list_buckets()

        # filter buckets
        buckets_list = [bucket for bucket in buckets_list if re.search(rf"{bucket_name}", bucket.name)]
    except Exception as e:
        buckets_list = []
        logger.error(f"{context.rid_get()} buckets list exception '{e}'")


    if "HX-Request" in request.headers:
        html_template = "buckets/list_table.html"
    else:
        html_template = "buckets/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            html_template,
            {
                "app_name": "Buckets",
                "app_version": app_version,
                "buckets_list": buckets_list,
                "prompt_text": "search",
            },
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} buckets list render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    logger.info(f"{context.rid_get()} buckets list ok")

    return response