from collections import defaultdict

from fastapi import APIRouter

#TODO Fix long imports
from src.config import get_settings
from src.models.request_models import SimilarityRequest
from src.models.response_models import SimilarityResponse

router = APIRouter()
settings = get_settings()


@router.post("/similarity/", response_model=SimilarityResponse)
async def calculate_similarity(request: SimilarityRequest):
    f"""
    Calculates the similarity between given protein sequences and finds homologous sequences in the database.

  
    Args:
    - sequences: A list of protein sequences with IDs.
        {settings.MAX_PROTEINS_PER_REQUEST} sequences are allowed in a single request.
        {settings.MAX_RESIDUE_COUNT} residues are allowed in a single protein sequence.
        {settings.MAX_RESIDUE_HEADER_LENGTH} characters are allowed in the header of a single protein sequence.
    - threshold: Similarity threshold (0.0-1.0).
    

    Please ensure that your request does not exceed these constraints.
    """
    # Your endpoint logic here
    response = defaultdict(dict)
    for sequence in request.sequences:
        response[sequence.id]["response_id_1"] = 0.1
        response[sequence.id]["response_id_2"] = 0.2
    sr = SimilarityResponse(homologous_sequences=response)
    return sr
