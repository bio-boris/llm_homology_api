from typing import Dict

from pydantic import BaseModel, Field


class SimilarityResponse(BaseModel):
    # A dictionary of protein sequences with their matched respective homologous sequences and their similarity scores.

    homologous_sequences: Dict[str, Dict[str, float]] = Field(
        ...,
        description="A dictionary of protein sequences with their matched respective homologous sequences and their similarity scores.",
    )

    class Config:
        schema_extra = {
            "example": {
                "homologous_sequences": {
                    "Protein1": {
                        "HomologousProteinA": 0.95,
                        "HomologousProteinB": 0.9,
                    },
                    "Protein2": {
                        "HomologousProteinC": 0.85,
                        "HomologousProteinD": 0.8,
                    },
                }
            }
        }


class ProteinSequenceResponse(BaseModel):
    # The unique identifier of the protein and the protein sequence.

    id: str = Field(..., description="The unique identifier of the protein.")
    embedding_distance: float = Field(
        ..., description="The calculated embedding distance for the protein."
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "ProteinX",
                "embedding_distance": 0.123,
            }
        }
