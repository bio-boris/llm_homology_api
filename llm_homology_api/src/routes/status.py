from fastapi import APIRouter, Request, Header, Cookie

from llm_homology_api.src.config import get_settings

router = APIRouter()

ALPHANUMERIC_PATTERN = r"^[a-zA-Z0-9]*$"


@router.get("/whoami")
def whoami(
    request: Request,
    authorization: str = Header(
        None,
        pattern=ALPHANUMERIC_PATTERN,
        alias="Authorization",
        description="KBase auth token",
    ),
    kbase_session: str = Cookie(None, pattern=ALPHANUMERIC_PATTERN),
):
    cac = request.app.state.auth_client

    return cac.validate_and_get_username_auth_roles(
        token=authorization if authorization else kbase_session
    )


@router.get("/")
@router.get("/status")
def status():
    settings = get_settings()
    return {
        "status": "ok",
        "version": settings.VERSION,
        "vcs_ref": settings.VCS_REF,
        "auth_url": settings.AUTH_URL,
    }
