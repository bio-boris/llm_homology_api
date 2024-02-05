from pydantic import BaseModel, constr, Field, conlist

from config import get_settings

settings = get_settings()


# TODO Uniqueness?
# TODO Regex validation of nucletides?
# TODO Ensuring the protein headers/ids are hashable


class ProteinSequence(BaseModel):
    id: constr(min_length=5, max_length=settings.MAX_RESIDUE_HEADER_LENGTH) = Field(
        ...,
        description=f"A unique identifier for the protein sequence, with a minimum length of 5 characters and a maximum length of "
        f"{settings.MAX_RESIDUE_HEADER_LENGTH}.",
    )
    sequence: constr(min_length=2, max_length=settings.MAX_RESIDUE_COUNT) = Field(
        ...,
        description=f"A protein sequence with a minimum length of 2 characters and a maximum length of "
        f"{settings.MAX_RESIDUE_COUNT}.",
    )


class SimilarityRequest(BaseModel):
    sequences: conlist(
        ProteinSequence, max_length=settings.MAX_PROTEINS_PER_REQUEST
    ) = Field(
        ...,
        description="A unique identifier for the protein sequence, with a minimum length of 5 characters and a maximum length of"
        f" {settings.MAX_RESIDUE_HEADER_LENGTH}.",
    )
    threshold: float = Field(..., description="Similarity threshold for LLM search")
