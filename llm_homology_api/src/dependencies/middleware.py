import logging

from fastapi import HTTPException
from fastapi import Header, Cookie
from fastapi.responses import JSONResponse
from starlette.requests import Request

from src.clients.CachedAuthClient import CachedAuthClient  # noqa: F401
from src.config import get_settings

# Constants
ALPHANUMERIC_PATTERN = r"^[a-zA-Z0-9]+$"


def is_authorized(
    request: Request,
    authorization: str = Header(
        None,
        pattern=ALPHANUMERIC_PATTERN,
        alias="Authorization",
        description="KBase auth token",
    ),
    kbase_session: str = Cookie(None, regex=ALPHANUMERIC_PATTERN),
    method: str | None = None,
    payload: dict | None = None,
) -> bool:
    """
    Check if the user is authorized to access the endpoint in general.
    This does not check if the user is authorized to STOP or VIEW LOGS for specific services.

    :param request: The request to check
    :param authorization: The authorization header
    :param kbase_session: The kbase_session cookie
    :param method: The method being called to log
    :return: A boolean indicating if the user is authorized or not
    """
    if not authorization and not kbase_session:
        logging.warning(
            f"No authorization header or kbase_session cookie provided for {method} payload: {payload}"
        )
        raise HTTPException(
            status_code=401,
            detail=f"Please provide the 'Authorization' header or 'kbase_session' cookie for {method} payload: {payload} ",
        )
    try:
        ac = request.app.state.auth_client  # type: CachedAuthClient
        return ac.is_authorized(token=authorization if authorization else kbase_session)
    except HTTPException as e:
        if e.status_code == 401:
            raise e
        elif e.status_code == 500:
            raise HTTPException(status_code=500, detail="Auth service is down")
        elif e.status_code == 404:
            raise e
        else:
            logging.warning("Invalid or expired token")
            raise HTTPException(status_code=400, detail="Invalid or expired token")


async def verify_request_size(request: Request, call_next):
    settings = get_settings()
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.MAX_REQUEST_SIZE:
        return JSONResponse(
            status_code=413, content={"detail": "Request body too large"}
        )
    response = await call_next(request)
    return response
