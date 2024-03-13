from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class HitDetail(BaseModel):
    Score: float = Field(
        ..., description="The similarity score of the homologous sequence."
    )
    Embedding: Optional[List[float]] = Field(
        None,
        description="The embedding vector associated with the homologous sequence, included based on a flag.",
    )


class QueryProtein(BaseModel):
    QueryId: str = Field(..., description="The identifier of the query protein.")
    Embedding: Optional[List[float]] = Field(
        None,
        description="The embedding vector associated with the query protein, included based on a flag.",
    )
    total_hits: int = Field(
        ...,
        description="The total number of homologous sequences found before trimming based on total hits and threshold.",
    )
    Hits: Dict[str, HitDetail] = Field(
        default_factory=dict,
        description="A dictionary of homologous sequences with their respective similarity scores and optional embeddings. Can be empty if none meet the score threshold.",
    )


class SimilarityResponse(BaseModel):
    proteins: List[QueryProtein] = Field(
        ...,
        description="A list of query proteins, each containing optional embedding vectors for the query protein, the total number of hits, and their homologous sequences information. The Hits list for each query protein could be empty.",
    )

    class Config:
        schema_extra = {
            "example": {
                "proteins": [
                    {
                        "QueryId": "QueryProtein1",
                        "Embedding": [
                            0.01,
                            0.02,
                            0.03,
                        ],  # Included or set to None based on the flag
                        "total_hits": 2,
                        "Hits": {
                            "HomologousProteinA": {
                                "Score": 0.95,
                                "Embedding": [
                                    0.1,
                                    0.2,
                                    0.3,
                                ],  # Included or set to None based on the flag
                            },
                            "HomologousProteinB": {
                                "Score": 0.9,
                                "Embedding": [
                                    0.4,
                                    0.5,
                                    0.6,
                                ],  # Included or set to None based on the flag
                            },
                        },
                    },
                    {
                        "QueryId": "QueryProtein2",
                        "Embedding": [
                            0.04,
                            0.05,
                            0.06,
                        ],  # Included or set to None based on the flag
                        "total_hits": 2,
                        "Hits": {
                            "HomologousProteinC": {
                                "Score": 0.85,
                                "Embedding": [
                                    0.7,
                                    0.8,
                                    0.9,
                                ],  # Included or set to None based on the flag
                            },
                            "HomologousProteinD": {
                                "Score": 0.8,
                                "Embedding": [
                                    1.0,
                                    1.1,
                                    1.2,
                                ],  # Included or set to None based on the flag
                            },
                        },
                    },
                    {
                        "QueryId": "QueryProtein3",
                        "Embedding": [
                            0.07,
                            0.08,
                            0.09,
                        ],  # Included or set to None based on the flag
                        "total_hits": 5,  # Indicates there were 5 hits found
                        "Hits": {},  # Empty because none meet the score threshold
                    },
                    # Additional query proteins could be listed here...
                ]
            }
        }
