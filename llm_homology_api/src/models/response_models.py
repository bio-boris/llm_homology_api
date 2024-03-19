from typing import List, Optional
from pydantic import BaseModel, Field


class HitDetail(BaseModel):
    HitID: str = Field(..., description="The unique identifier of the homologous sequence.")
    Score: float = Field(..., description="The similarity score of the homologous sequence.")
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
        description="The total number of homologous sequences found after trimming based on max hits and threshold score.",
    )
    Hits: List[HitDetail] = Field(
        default_factory=list,
        description="A list of homologous sequences with their respective similarity scores and optional embeddings. Can be empty if none meet the score threshold.",
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
                        "Embedding": [0.01, 0.02, 0.03],
                        "total_hits": 4,
                        "Hits": [
                            {
                                "HitID": "HomologousProteinA",
                                "Score": 0.95,
                                "Embedding": [0.1, 0.2, 0.3],
                            },
                            {
                                "HitID": "HomologousProteinB",
                                "Score": 0.92,
                                "Embedding": [0.4, 0.5, 0.6],
                            },
                            {
                                "HitID": "HomologousProteinC",
                                "Score": 0.88,
                                "Embedding": [0.7, 0.8, 0.9],
                            },
                            {
                                "HitID": "HomologousProteinD",
                                "Score": 0.85,
                                "Embedding": [1.0, 1.1, 1.2],
                            },
                        ],
                    },
                    {
                        "QueryId": "QueryProtein2",
                        "Embedding": [0.04, 0.05, 0.06],
                        "total_hits": 3,
                        "Hits": [
                            {
                                "HitID": "HomologousProteinE",
                                "Score": 0.93,
                                "Embedding": [0.11, 0.22, 0.33],
                            },
                            {
                                "HitID": "HomologousProteinF",
                                "Score": 0.89,
                                "Embedding": [0.44, 0.55, 0.66],
                            },
                            {
                                "HitID": "HomologousProteinG",
                                "Score": 0.87,
                                "Embedding": [0.77, 0.88, 0.99],
                            },
                        ],
                    },
                    {
                        "QueryId": "QueryProtein3",
                        "Embedding": [0.07, 0.08, 0.09],
                        "total_hits": 2,
                        "Hits": [
                            {
                                "HitID": "HomologousProteinH",
                                "Score": 0.91,
                                "Embedding": [0.12, 0.23, 0.34],
                            },
                            {
                                "HitID": "HomologousProteinI",
                                "Score": 0.86,
                                "Embedding": [0.45, 0.56, 0.67],
                            },
                        ],
                    },
                    # Additional query proteins could be listed here...
                ]
            }
        }
