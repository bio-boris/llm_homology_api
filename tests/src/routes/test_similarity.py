# test similarity route
# test fastapi route
from fastapi import APIRouter

from llm_homology_api.src.routes.similarity import router as similarity_router
from llm_homology_api.src.routes.status import router as status_router

from fastapi.testclient import TestClient

from llm_homology_api.src.factory import create_app  # Adjust the import path according to your project structure
from llm_homology_api.src.config import get_settings


def test_routers():
    assert isinstance(similarity_router, APIRouter)
    assert isinstance(status_router, APIRouter)
    assert similarity_router.url_path_for("calculate_similarity") == "/similarity/"
    assert status_router.url_path_for("status") == "/status/"
    assert status_router.url_path_for("whoami") == "/whoami/"


settings = get_settings()
app = create_app()
client = TestClient(create_app())


def test_calculate_similarity():
    # Sample request payload
    request_payload = {
        "sequences": [
            {"id": "Protein1", "sequence": "MKT..."},
            {"id": "Protein2", "sequence": "AGT..."}
        ],
        "threshold": 0.5
    }

    # Make a POST request to the endpoint
    response = client.post("/similarity/", json=request_payload)

    # Check if the status code is 200
    assert response.status_code == 200

    # Optionally, check the structure and data of the response
    data = response.json()
    assert "homologous_sequences" in data
    assert isinstance(data["homologous_sequences"], dict)
    # Further checks can be added based on the expected logic and output


def test_similarity_request_constraints():
    # Test exceeding the maximum number of sequences per request
    request_payload = {
        "sequences": [{"id": f"Protein{i}", "sequence": "MKT..."} for i in range(settings.MAX_PROTEINS_PER_REQUEST + 1)],
        "threshold": 0.5
    }

    response = client.post("/similarity/", json=request_payload)

    # Expecting a 422 Unprocessable Entity response due to validation error
    assert response.status_code == 422
    # Add more tests as needed, such as testing for maximum sequence length, etc.
