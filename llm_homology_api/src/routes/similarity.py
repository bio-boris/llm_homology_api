from collections import defaultdict

from fastapi import APIRouter

# TODO Fix long imports
from config import get_settings
from models.request_models import SimilarityRequest
from models.response_models import SimilarityResponse

router = APIRouter()
settings = get_settings()


@router.post("/similarity", response_model=SimilarityResponse)
async def calculate_similarity(request: SimilarityRequest):
    f"""
    Calculates the similarity between given protein sequences and finds homologous sequences in the database.

  
    Args:
    - sequences: A list of protein sequences with IDs.
        {settings.MAX_PROTEINS_PER_REQUEST} sequences are allowed in a single request.
        {settings.MAX_RESIDUE_COUNT} residues are allowed in a single protein sequence. After 1200 characters, 
        the sequence is truncated.. So maybe we want to reduce the max length
        {settings.MAX_RESIDUE_HEADER_LENGTH} characters are allowed in the header of a single protein sequence. 
    - threshold: Similarity threshold (0.0-1.0).
    

    Please ensure that your request does not exceed these constraints.
    """
    # Your endpoint logic here
    response = defaultdict(dict)
    sequences = [sequence.sequence for sequence in request.sequences]

    ss = request.state.ss

    results = ss.search(request.sequences, top_k=1)

    # Print the results
    for score, ind in zip(results.total_scores, results.total_indices):
        # Get the sequence tags found by the search
        found_tags = ss.get_sequence_tags(ind)
        print(f'scores: {score}, indices: {ind}, tags: {found_tags}')

    # all_seqs = [sequence.sequence for sequence in request.sequences]
    sr = SimilarityResponse(homologous_sequences=response)
    return sr
