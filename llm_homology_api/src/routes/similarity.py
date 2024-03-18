from fastapi import APIRouter, Request

from config import get_settings
from models.request_models import SimilarityRequest
from models.response_models import SimilarityResponse, QueryProtein, HitDetail

router = APIRouter()
settings = get_settings()


async def process_hits(search_results, threshold, discard_embeddings, ss):
    pruned_hits = []
    for scores, indices in zip(search_results.total_scores, search_results.total_indices):
        seq_ids = ss.get_sequence_tags(indices)
        embeddings = [] if discard_embeddings else ss.get_sequence_embeddings(indices)

        pruned_result = [
            HitDetail(HitID=seq_id, Score=score, Embedding=[] if discard_embeddings else list(map(float, embedding)))
            for seq_id, score, embedding in zip(seq_ids, scores, embeddings) if score >= threshold
        ]
        pruned_hits.append(pruned_result)
    return pruned_hits


@router.post("/similarity", response_model=SimilarityResponse)
async def calculate_similarity(request: Request, similarity_request: SimilarityRequest):
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
    query_sequences = [sequence.sequence for sequence in similarity_request.sequences]
    search_results, query_embeddings = request.app.state.ss.search(query_sequences, top_k=similarity_request.max_hits)

    pruned_hits = await process_hits(search_results, similarity_request.threshold, similarity_request.discard_embeddings, request.app.state.ss)

    if not similarity_request.discard_embeddings:
        query_embeddings = [list(map(float, e)) for e in query_embeddings]

    proteins = [
        QueryProtein(
            QueryId=sequence.id,
            Embedding=query_embeddings[i] if not similarity_request.discard_embeddings else [],
            total_hits=1,
            Hits=hits
        ) for i, (sequence, hits) in enumerate(zip(similarity_request.sequences, pruned_hits))
    ]

    return SimilarityResponse(proteins=proteins)


# @router.post("/similarity", response_model=SimilarityResponse)
# async def calculate_similarity(request: Request, sr: SimilarityRequest):
#     f"""
#     Calculates the similarity between given protein sequences and finds homologous sequences in the database.
#
#
#     Args:
#     - sequences: A list of protein sequences with IDs.
#         {settings.MAX_PROTEINS_PER_REQUEST} sequences are allowed in a single request.
#         {settings.MAX_RESIDUE_COUNT} residues are allowed in a single protein sequence. After 1200 characters,
#         the sequence is truncated.. So maybe we want to reduce the max length
#         {settings.MAX_RESIDUE_HEADER_LENGTH} characters are allowed in the header of a single protein sequence.
#     - threshold: Similarity threshold (0.0-1.0).
#
#
#     Please ensure that your request does not exceed these constraints.
#     """
#     discard_embeddings = sr.discard_embeddings
#     query_sequences = [sequence.sequence for sequence in sr.sequences]
#     threshold = sr.threshold
#     top_k = sr.max_hits
#
#     ss = (
#         request.app.state.ss
#     )  # SimilaritySearch instance, can I reuse it between queries?
#
#     search_results, query_embeddings = ss.search(query_sequences, top_k=top_k)
#
#     pruned_hits = []
#     for scores, indices in zip(search_results.total_scores, search_results.total_indices):
#         # Look up sequence ids for each hit
#         seq_ids = ss.get_sequence_tags(indices)
#
#         # Look up embeddings for each hit
#         if not discard_embeddings:
#             embeddings = ss.get_sequence_embeddings(indices)
#             embeddings = [list(map(float, e)) for e in embeddings]
#
#         pruned_result = []
#         for idx, (seq_id, score) in enumerate(zip(seq_ids, scores)):
#             if score >= threshold:
#                 embedding = [] if discard_embeddings else embeddings[idx]
#                 pruned_result.append(
#                     HitDetail(HitID=seq_id, Score=score, Embedding=embedding)
#                 )
#         pruned_hits.append(pruned_result)
#
#     # Convert embeddings to list of lists of floats
#     if not discard_embeddings:
#         query_embeddings = [list(map(float, e)) for e in query_embeddings]
#
#     proteins = []
#     for i, protein in enumerate(sr.sequences):
#         qp = QueryProtein(
#             QueryId=protein.id,
#             Embedding=query_embeddings[i] if not discard_embeddings else [],
#             total_hits=1,
#             Hits=pruned_hits[i],
#         )
#         proteins.append(qp)
#
#     return SimilarityResponse(proteins=proteins)
