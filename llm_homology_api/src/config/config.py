from functools import lru_cache

from pydantic_settings import BaseSettings


class LLMHomologyApiSettings(BaseSettings):
    """Settings for the LLM Homology API taken from the environment"""

    MAX_RESIDUE_HEADER_LENGTH: int = 100  # The maximum length of the protein sequence header
    MAX_RESIDUE_COUNT: int = 5000  # The maximum number of residues allowed in a single protein sequence
    MAX_PROTEINS_PER_REQUEST: int = 500  # The maximum number of protein sequences allowed in a single request

    MAX_REQUEST_SIZE: int = 2805000  # Not yet implemented
    VERSION: str
    ROOT_PATH: str
    AUTH_URL: str
    ADMIN_ROLES: list = ["LLMHomologyAdmin"]
    VCS_REF: str
    MODEL_DIR: str

    class Config:
        extra = "forbid"


@lru_cache(maxsize=None)
def get_settings() -> LLMHomologyApiSettings:
    return LLMHomologyApiSettings()
