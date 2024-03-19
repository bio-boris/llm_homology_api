import os

from cacheout import LRUCache
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from clients.CachedAuthClient import CachedAuthClient
from config.config import LLMHomologyApiSettings
from routes.similarity import router as similarity_router
from routes.status import router as whoami_router
from ss_factory import setup_similarity_search


def create_app(
    cached_auth_client=None,
    valid_tokens_cache=None,
    admin_roles=None,
    auth_url=None,
    ss_dataset_dir=None,
):

    cfg = LLMHomologyApiSettings()
    # Required to be set to "" to get docs working for local development
    root_path = cfg.ROOT_PATH if cfg.ROOT_PATH != "" else None
    model_dir = cfg.MODEL_DIR if cfg.MODEL_DIR != "" else None

    app = FastAPI(
        title="LLM Homology API",
        description="API for LLM Homology",
        version=cfg.VERSION,
        root_path=root_path,
        # exception_handlers={
        #     errors.CollectionError: _handle_app_exception,
        #     RequestValidationError: _handle_fastapi_validation_exception,
        #     StarletteHTTPException: _handle_http_exception,
        #     Exception: _handle_general_exception
        # },
        # responses={
        #     "4XX": {"model": models_errors.ClientError},
        #     "5XX": {"model": models_errors.ServerError}
        # }
    )
    app.add_middleware(GZipMiddleware)
    app.include_router(whoami_router, tags=["whoami"])
    app.include_router(similarity_router, tags=["similarity"])

    # app.include_router(ROUTER_DANGER)

    # app.add_event_handler("startup", build_app_wrapper)

    # async def clean_app_wrapper():
    #     await app_state.destroy_app_state(app)

    # app.add_event_handler("shutdown", clean_app_wrapper)
    if valid_tokens_cache is None:
        valid_tokens_cache = LRUCache(ttl=10)

    if admin_roles is None:
        admin_roles = cfg.ADMIN_ROLES

    if auth_url is None:
        auth_url = cfg.AUTH_URL

    if cached_auth_client is None:
        cached_auth_client = CachedAuthClient(
            valid_tokens_cache=valid_tokens_cache,
            auth_url=auth_url,
            admin_roles=admin_roles,
        )

    app.state.auth_client = cached_auth_client
    # if os.environ.get("DEBUG", 1) == 1:
    #     app.state.ss = None
    # else:
    app.state.ss = setup_similarity_search(model_dir)
    return app
