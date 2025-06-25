import os
import time

import fastapi
import fastapi.responses
import fastapi.templating

import context
import log
import main_shared
import services.anthropic
import services.anthropic.tools

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers")

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

app_version = os.environ["APP_VERSION"]


@app.get("/tools", response_class=fastapi.responses.HTMLResponse)
def tools_query(
    request: fastapi.Request,
    query: str = "",
):
    """ """
    logger.info(f"{context.rid_get()} tools query '{query}' try")
    query_code = 0
    query_error = ""
    query_ok = ""
    query_response = ""

    try:
        if query:
            t_start = time.time()
            anthropic_message = services.anthropic.query_tools(query=query, tools=services.anthropic.tools.list())
            t_secs = round(time.time() - t_start, 2)

            query_response = anthropic_message.content[0].text
            query_ok = f"anthropic query completed in {t_secs}s"
    except Exception as e:
        logger.error(f"{context.rid_get()} tools query exception '{e}'")
        query_code = 500
        query_response = str(e)

    logger.info(f"{context.rid_get()} tools query ok")

    if "HX-Request" in request.headers:
        html_template = "tools/query_fragment.html"
    else:
        html_template = "tools/query.html"

    try:
        response = templates.TemplateResponse(
            request,
            html_template,
            {
                "app_name": "Tools",
                "app_version": app_version,
                "query": query,
                "query_code": query_code,
                "query_error": query_error,
                "query_ok": query_ok,
                "query_prompt": "question",
                "query_response": query_response,
            },
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} tools query render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    if "HX-Request" in request.headers:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?query={query}"

    return response
