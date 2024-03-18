from fastapi import APIRouter, Request

from config import get_settings
from models.request_models import SimilarityRequest
from models.response_models import SimilarityResponse, QueryProtein, HitDetail

router = APIRouter()
settings = get_settings()


@router.post("/similarity", response_model=SimilarityResponse)
async def calculate_similarity(request: Request, sr: SimilarityRequest):
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
    discard_embeddings = sr.discard_embeddings
    query_sequences = [sequence.sequence for sequence in sr.sequences]
    threshold = sr.threshold
    top_k = sr.max_hits

    ss = request.app.state.ss  # SimilaritySearch instance

    search_results, query_embeddings = ss.search(query_sequences, top_k=top_k)

    pruned_hits = []
    for score, ind in zip(search_results.total_scores, search_results.total_indices):
        pruned_result = []
        seq_id = ss.get_sequence_tags(ind)

        for i in range(len(score)):
            embedding = []
            if not discard_embeddings:
                embedding = ss.get_sequence_embeddings(ind)
                # Convert to python list for REST API
                embedding = [float(idx) for idx in embedding[i].tolist()]

            pruned_result.append(HitDetail(HitID=seq_id[i], Score=score[i], Embedding=embedding))
            pruned_hits.append(pruned_result)

    proteins = []
    for i, protein in enumerate(sr.sequences):
        qp = QueryProtein(
            QueryId=protein.id,
            Embedding=query_embeddings[i] if not discard_embeddings else [],
            total_hits=1,
            Hits=pruned_hits[i],
        )
        proteins.append(qp)

    return SimilarityResponse(proteins=proteins)
