# # test similarity route
# # test fastapi route
import copy

from fastapi import APIRouter
from fastapi.testclient import TestClient

from config import get_settings
from factory import (
    create_app,
)  # Adjust the import path according to your project structure
from routes.similarity import router as similarity_router
from routes.status import router as status_router

settings = get_settings()
app = create_app()
client = TestClient(create_app())


def test_routers():
    assert isinstance(similarity_router, APIRouter)
    assert isinstance(status_router, APIRouter)
    assert similarity_router.url_path_for("calculate_similarity") == "/similarity"
    assert status_router.url_path_for("status") == "/status"
    assert status_router.url_path_for("whoami") == "/whoami"


def test_calculate_similarity():
    request_payload = {
        "sequences": [
            {
                "id": ">Q5HAN0",
                "sequence": "MCTSIRHDWQLPEVLELFNLPFNDLILNAHLIHRKFFNSNEIQIAGLLNIKTGGCPENCKYCSQSAHYKTQLKKEDLLNIETIKEAIKKAKVNGIDRFCFAAAWRQIRDRDIEYICNIISLIKSENLESCASLGMVTLEQAKKLKTAGLDFYNHNIDTSRDFYYNVTTTRSYDDRLSSLNNISEAEINICSGGILGLGESIEDRAKMLLTLANLKKHPKSVPINRLVPIKGTPFENNPKISNIDFIRTIAVARILMPESYVRLAAGRESMSHEMQALCLFAGANSLFYGEKLLTTPNADCNDDKNLLSKLGVKTKQAVFFDS",
            },
            {
                "id": ">Q5HAN0",
                "sequence": "MCTSIRHDWQLPEVLELFNLPFNDLILNAHLIHRKFFNSNEIQIAGLLNIKTGGCPENCKYCSQSAHYKTQLKKEDLLNIETIKEAIKKAKVNGIDRFCFAAAWRQIRDRDIEYICNIISLIKSENLESCASLGMVTLEQAKKLKTAGLDFYNHNIDTSRDFYYNVTTTRSYDDRLSSLNNISEAEINICSGGILGLGESIEDRAKMLLTLANLKKHPKSVPINRLVPIKGTPFENNPKISNIDFIRTIAVARILMPESYVRLAAGRESMSHEMQALCLFAGANSLFYGEKLLTTPNADCNDDKNLLSKLGVKTKQAVFFDS",
            }
        ],
        "threshold": 0.8,
        "max_hits": 2,
        "discard_embeddings": True,
    }
    # response = client.post("/similarity/", json=request_payload)
    # assert response.status_code == 200
    # data = response.json()
    # assert data == {
    #     "proteins": [
    #         {
    #             "Embedding": [],
    #             "Hits": [
    #                 {"Embedding": [], "HitID": "Q5HAN0", "Score": 0.9999954700469971},
    #                 {"Embedding": [], "HitID": "Q5FFY2", "Score": 0.9999621510505676},
    #             ],
    #             "QueryId": ">Q5HAN0",
    #             "total_hits": 2,
    #         }
    #     ]
    # }

    # Get embeddings
    request_payload2 = copy.copy(request_payload)
    request_payload2["discard_embeddings"] = False
    response = client.post("/similarity/", json=request_payload2)
    assert response.status_code == 200
    data = response.json()
    assert data["proteins"][0]["Hits"][0]["Embedding"] == data["proteins"][1]["Hits"][0]["Embedding"]

    for i in range(2):
        assert len(data["proteins"][i]["Embedding"]) == 1280
        assert len(data["proteins"][i]["Hits"][0]["Embedding"]) == 1280
        assert len(data["proteins"][i]["Hits"][1]["Embedding"]) == 1280
        assert data["proteins"][i]["total_hits"] == 2
        assert data["proteins"][i]["QueryId"] == ">Q5HAN0"
        assert data["proteins"][i]["Hits"][0]["HitID"] == "Q5HAN0"
        assert data["proteins"][i]["Hits"][0]["Score"] == 0.9999958276748657
        assert data["proteins"][i]["Hits"][1]["HitID"] == "Q5FFY2"
        assert data["proteins"][i]["Hits"][1]["Score"] == 0.9999616742134094








#
# def test_calculate_similarity():
#     # Sample request payload
#     request_payload = {
#         "sequences": [
#             {"id": "Protein1", "sequence": "MKT..."},
#             {"id": "Protein2", "sequence": "AGT..."},
#         ],
#         "threshold": 0.5,
#     }
#
#     # Make a POST request to the endpoint
#     response = client.post("/similarity/", json=request_payload)
#
#     # Check if the status code is 200
#     assert response.status_code == 200
#
#     # Optionally, check the structure and data of the response
#     data = response.json()
#     assert "homologous_sequences" in data
#     assert isinstance(data["homologous_sequences"], dict)
#     # Further checks can be added based on the expected logic and output
#
#
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
