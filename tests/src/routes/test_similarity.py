# # test similarity route
# # test fastapi route
from unittest.mock import MagicMock

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from config import get_settings
from factory import (
    create_app,
)  # Adjust the import path according to your project structure
from routes.similarity import router as similarity_router, get_filtered_annotations
from routes.status import router as status_router

settings = get_settings()
app = create_app()
client = TestClient(create_app())

seq1 = {
    "id": ">Q5HAN0",
    "sequence": "MCTSIRHDWQLPEVLELFNLPFNDLILNAHLIHRKFFNSNEIQIAGLLNIKTGGCPENCKYCSQSAHYKTQLKKEDLLNIETIKEAIKKAKVNGIDRFCFAAAWRQIRDRDIEYICNIISLIKSENLESCASLGMVTLEQAKKLKTAGLDFYNHNIDTSRDFYYNVTTTRSYDDRLSSLNNISEAEINICSGGILGLGESIEDRAKMLLTLANLKKHPKSVPINRLVPIKGTPFENNPKISNIDFIRTIAVARILMPESYVRLAAGRESMSHEMQALCLFAGANSLFYGEKLLTTPNADCNDDKNLLSKLGVKTKQAVFFDS",
}
seq2 = {
    "id": ">Q5AYI7",
    "sequence": "MSVSFTRSFPRAFIRSYGTVQSSPTAASFASRIPPALQEAVAATAPRTNWTRDEVQQIYETPLNQLTYAAAAVHRRFHDPSAIQMCTLMNIKTGGCSEDCSYCAQSSRYSTGLKATKMSPVDDVLEKARIAKANGSTRFCMGAAWRDMRGRKTSLKNVKQMVSGVREMGMEVCVTLGMIDADQAKELKDAGLTAYNHNLDTSREFYPTIITTRSYDERLKTLSHVRDAGINVCSGGILGLGEADSDRIGLIHTVSSLPSHPESFPVNALVPIKGTPLGDRKMISFDKLLRTVATARIVLPATIVRLAAGRISLTEEQQVACFMAGANAVFTGEKMLTTDCNGWDEDRAMFDRWGFYPMRSFEKETNAATPQQHVDSVAHESEKNPAAPAAEAL",
}

MAX_EMBEDDING_LENGTH = 1280


def test_routers():
    assert isinstance(similarity_router, APIRouter)
    assert isinstance(status_router, APIRouter)
    assert similarity_router.url_path_for("calculate_similarity") == "/similarity"
    assert status_router.url_path_for("status") == "/status"
    assert status_router.url_path_for("whoami") == "/whoami"


# @pytest.mark.skip(reason="Not yet implemented")
@pytest.mark.parametrize(
    "discard_embeddings,threshold,max_hits,expected_total_hits,expected_embedding_length",
    [
        (True, 0.99996, 500, 2, None),  # Expect 1 hits, no embeddings
        (True, 0.99, 10, 10, None),  # Expect 10 hits, no embeddings
        (False, 0.99996, 500, 2, MAX_EMBEDDING_LENGTH),  # Expect 1 hits, w embeddings
    ],
)
def test_calculate_similarity_w_duplicates(
    discard_embeddings, threshold, max_hits, expected_total_hits, expected_embedding_length
):
    request_payload = {
        "sequences": [seq1, seq1],  # Ensure ability to handle duplicate sequence ids
        "threshold": threshold,
        "max_hits": max_hits,
        "discard_embeddings": discard_embeddings,
    }
    response = client.post("/similarity/", json=request_payload)
    assert response.status_code == 200
    data = response.json()

    # Parameterized assertions
    for protein in data["proteins"]:
        assert len(protein["Hits"]) == protein["total_hits"]
        assert protein["total_hits"] == expected_total_hits
        if expected_embedding_length:
            assert len(protein["Embedding"]) == expected_embedding_length
            for hit in protein["Hits"]:
                assert len(hit["Embedding"]) == expected_embedding_length
        else:
            assert protein.get("Embedding") == [] and len(protein["Embedding"]) == 0
            for hit in protein["Hits"]:
                assert hit.get("Embedding") == [] and len(hit["Embedding"]) == 0


def test_calculate_similarity_with_2_sequences_discard_embeddings():
    request_payload = {
        "sequences": [seq1, seq2],
        "threshold": 0.99996,
        "max_hits": 500,
        "discard_embeddings": True,
    }
    response = client.post("/similarity/", json=request_payload)
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "proteins": [
            {
                "Embedding": [],
                "Hits": [
                    {"Embedding": [], "HitID": "Q5HAN0", "Score": 0.9999960660934448},
                    {"Embedding": [], "HitID": "Q5FFY2", "Score": 0.9999607801437378},
                ],
                "QueryId": ">Q5HAN0",
                "total_hits": 2,
            },
            {
                "Embedding": [],
                "Hits": [{"Embedding": [], "HitID": "Q5AYI7", "Score": 0.9999743700027466}],
                "QueryId": ">Q5AYI7",
                "total_hits": 1,
            },
        ]
    }


def test_calculate_similarity_with_2_sequences_keep_embeddings():
    request_payload = {
        "sequences": [seq1, seq2],
        "threshold": 0.99996,
        "max_hits": 500,
        "discard_embeddings": False,
    }
    response = client.post("/similarity/", json=request_payload)
    assert response.status_code == 200
    data = response.json()
    # Ensure that query sequence embeddings are not duplicates!
    assert data["proteins"][0]["Embedding"] != data["proteins"][1]["Embedding"]
    # Ensure that hit sequence embeddings are not duplicates!
    assert data["proteins"][0]["Hits"][0]["Embedding"] != data["proteins"][0]["Hits"][1]["Embedding"]
    assert data["proteins"][1]["Hits"][0]["Embedding"] != data["proteins"][0]["Hits"][0]["Embedding"]
    assert data["proteins"][1]["Hits"][0]["Embedding"] != data["proteins"][0]["Hits"][1]["Embedding"]
    # Ensure that embeddings are lists of floats
    for protein in data["proteins"]:
        assert len(protein["Embedding"]) == MAX_EMBEDDING_LENGTH
        for hit in protein["Hits"]:
            assert len(hit["Embedding"]) == MAX_EMBEDDING_LENGTH
            assert isinstance(hit["Embedding"], list)
            for e in hit["Embedding"]:
                assert isinstance(e, float)


def test_get_filtered_annotations():
    # Mock inputs
    hit_indices = [1, 2, 3]
    hit_scores = [0.9, 0.95, 0.85]
    threshold = 0.9

    # Expected outputs for both scenarios
    expected_filtered_scores = [0.9, 0.95]  # Only scores >= threshold
    expected_filtered_tags = ["Tag1", "Tag2"]  # Corresponding tags for hit indices [1, 2]

    # Mock the SimilaritySearch instance's methods
    mock_ss = MagicMock()
    mock_ss.get_sequence_tags.side_effect = lambda indices: ["Tag0", "Tag1", "Tag2", "Tag3"][
        min(indices) : max(indices) + 1
    ]
    mock_ss.get_sequence_embeddings.side_effect = lambda indices: [[0.0, 0.1], [0.1, 0.2], [0.3, 0.4], [0.5, 0.6]][
        min(indices) : max(indices) + 1
    ]

    # Test case when discard_embeddings is False
    discard_embeddings = False
    filtered_scores, filtered_tags, filtered_embeddings = get_filtered_annotations(
        hit_indices, hit_scores, threshold, discard_embeddings, mock_ss
    )

    # Assertions when embeddings are not discarded
    assert filtered_scores == expected_filtered_scores
    assert filtered_tags == expected_filtered_tags

    # Test case when discard_embeddings is True
    discard_embeddings = True
    _, _, filtered_embeddings_discard = get_filtered_annotations(
        hit_indices, hit_scores, threshold, discard_embeddings, mock_ss
    )

    # Assertions when embeddings are discarded
    assert filtered_embeddings_discard == [], "Embeddings were not discarded as expected"


# def test_similarity_request_constraints():
#     # Test exceeding the maximum number of sequences per request
#     request_payload = {
#         "sequences": [
#             {"id": f"Protein{i}", "sequence": "MKT..."}
#             for i in range(settings.MAX_PROTEINS_PER_REQUEST + 1)
#         ],
#         "threshold": 0.5,
#     }
#
#     response = client.post("/similarity/", json=request_payload)
#
#     # Expecting a 422 Unprocessable Entity response due to validation error
#     assert response.status_code == 422
#     # Add more tests as needed, such as testing for maximum sequence length, etc.
