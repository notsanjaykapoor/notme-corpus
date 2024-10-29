import os
import typing

import contextlib
import fastapi
import fastapi.middleware.cors
import fastapi.staticfiles
import fastapi.templating
import sqlmodel
import starlette.middleware.sessions
import ulid

import dot_init  # noqa: F401

import context  # noqa: E402
import log  # noqa: E402
import models  # noqa: E402
import routers
import services.database.session  # noqa: E402

logger = log.init("app")


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    logger.info("api.startup init")

    # migrate database
    services.database.session.migrate()

    logger.info("api.startup completed")

    yield


# create app object
app = fastapi.FastAPI(lifespan=lifespan)

app.mount("/static", fastapi.staticfiles.StaticFiles(directory="static"), name="static")

# db dependency
def get_db():
    with services.database.session.get() as session:
        yield session


# gql db dependency
async def get_gql_context(db=fastapi.Depends(get_db)):
    return {"db": db}


# app.include_router(routers.admin.app)
app.include_router(routers.corpus.app)
app.include_router(routers.health.app)
app.include_router(routers.images.app)
app.include_router(routers.rag.app)
app.include_router(routers.workq.app)

app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    starlette.middleware.sessions.SessionMiddleware,
    secret_key=os.environ.get("FASTAPI_SESSION_KEY"),
    max_age=None,
)


@app.middleware("http")
async def add_request_id(request: fastapi.Request, call_next):
    # set request id context var
    context.rid_set(ulid.new().str)
    response = await call_next(request)
    return response


@app.get("/favicon.ico")
def favicon():
    file_name = "favicon.ico"
    file_path = os.path.join(app.root_path, "static", file_name)
    return fastapi.responses.FileResponse(
        path=file_path,
        headers={"Content-Disposition": "attachment; filename=" + file_name},
    )


@app.get("/")
def home():
    return fastapi.responses.RedirectResponse("/corpus")


@app.get("/openid/auth")
def openid_login(
    db: sqlmodel.Session = fastapi.Depends(get_db),
    email: typing.Optional[str] = "",
    idp: typing.Optional[str] = "",
):
    logger.info(f"{context.rid_get()} openid.auth")

    if email:
        # map email to idp
        struct_list = services.users.List(
            db=db, query=f"email:{email}", offset=0, limit=1
        ).call()

        if struct_list.code != 0:
            return {"code": 409, "errors": ["user not found"]}

        idp = struct_list.objects[0].idp

    if not idp:
        return {"code": 422, "errors": ["idp is required"]}

    # map idp to auth uri

    struct_auth = services.openid.AuthUriGet(idp=idp).call()

    if struct_auth.code != 0:
        return {"code": struct_auth.code, "errors": struct_auth.errors}

    return {"code": 0, "uri": struct_auth.uri, "idp": idp}


@app.get("/openid/authentik/callback")
def openid_authentik_callback(request: fastapi.Request, state: str, code: str):
    logger.info(f"{context.rid_get()} openid.authentik.callback try")

    struct_auth = services.openid.AuthCallback(
        idp="authentik", code=code, state=state
    ).call()

    if struct_auth.code == 0:
        request.session["user_jwt"] = struct_auth.token
        request.session["user_email"] = struct_auth.email

    logger.info(f"{context.rid_get()} openid.authentik.callback completed")

    return {
        "code": struct_auth.code,
        "errors": struct_auth.errors,
    }


@app.get("/openid/google/callback")
def openid_google_callback(request: fastapi.Request, state: str, code: str):
    logger.info(f"{context.rid_get()} openid.google.callback try")

    struct_auth = services.openid.AuthCallback(
        idp="google", code=code, state=state
    ).call()

    logger.info(f"{context.rid_get()} openid.google.callback completed")

    return {
        "code": struct_auth.code,
        "errors": struct_auth.errors,
    }
