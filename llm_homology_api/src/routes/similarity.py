import logging

import protein_search.search
from fastapi import APIRouter, Request
from protein_search.search import BatchedSearchResults

from config import get_settings
from models.request_models import SimilarityRequest
from models.response_models import SimilarityResponse, QueryProtein, HitDetail

import functools

router = APIRouter()
settings = get_settings()


logging.basicConfig(level=logging.INFO)


@functools.lru_cache(maxsize=100000)
def get_cached_embedding(ss, index):
    logging.info(f"missed embedding cache for index {index}")
    return ss.get_sequence_embeddings([index])[0]


@functools.lru_cache(maxsize=100000)
def get_cached_tag(ss, index):
    logging.info(f"missed tag cache for index {index}")
    return ss.get_sequence_tags([index])[0]


"""
Optimization: Depending on the size of hit_indices and hit_scores, and how often this function is called, you might be iterating multiple times over these lists (once for filtering scores and once for indices). You could consider combining these operations into a single loop to optimize performance, especially if the lists are large.

Error Handling: Consider what should happen if hit_indices and hit_scores have different lengths. This could indicate a mismatch in data alignment and might warrant an additional validation check at the start of the function.
"""


def get_filtered_annotations(
    hit_indices: list[int],
    hit_scores: list[float],
    threshold: float,
    discard_embeddings: bool,
    ss: protein_search.search.SimilaritySearch,
) -> tuple[list[float], list[str], list[list[float]]]:
    """
    Get the filtered sequence tags and embeddings based on the similarity threshold and discard_embeddings flag.
    @param hit_indices: Indices of the hits in the database.
    @param hit_scores: Similarity scores for the hits.
    @param threshold: Similarity threshold for pruning the search results.
    @param discard_embeddings: Determine whether to discard the embeddings of the queries and hits.
    @param ss: SimilaritySearch object used for searching.

    """
    # Keep hits with scores above the threshold
    filtered_indices = [idx for idx, score in zip(hit_indices, hit_scores) if score >= threshold]
    filtered_scores = [score for score in hit_scores if score >= threshold]

    # Retrieve only filtered sequence tags and embeddings with scores above the threshold:

    # filtered_sequence_tags = ss.get_sequence_tags(filtered_indices)
    filtered_sequence_tags = [get_cached_tag(ss, idx) for idx in filtered_indices]

    # filtered_embeddings = [] if discard_embeddings else ss.get_sequence_embeddings(filtered_indices)
    filtered_embeddings = [] if discard_embeddings else [get_cached_embedding(ss, idx) for idx in filtered_indices]

    if len(filtered_scores) != len(filtered_sequence_tags):
        raise ValueError(
            f"Length of filtered scores and sequence tags do not match. Got {len(filtered_scores)} and {len(filtered_sequence_tags)}"
        )

    if not discard_embeddings:
        if len(filtered_scores) != len(filtered_embeddings):
            raise ValueError(
                f"Length of filtered scores and embeddings do not match. Got {len(filtered_scores)} and {len(filtered_embeddings)}"
            )

        if len(filtered_sequence_tags) != len(filtered_embeddings):
            raise ValueError(
                f"Length of filtered sequence tags and embeddings do not match. Got {len(filtered_sequence_tags)} and {len(filtered_embeddings)}"
            )

    return filtered_scores, filtered_sequence_tags, filtered_embeddings


def process_hits(
    search_results: protein_search.search.BatchedSearchResults,
    threshold: float,
    discard_embeddings: bool,
    ss: protein_search.search.SimilaritySearch,
) -> list[list[HitDetail]]:
    """
    Process the search results to prune the hits based on the similarity threshold and discard_embeddings flag.
    @param search_results: BatchedSearchResults object containing the search results.
    @param threshold: Similarity threshold for pruning the search results.
    @param discard_embeddings: Whether to discard the embeddings of the queries and hits.
    @param ss: SimilaritySearch object used for searching.
    @return: Pruned hits for each query sequence.
    @rtype: list[list[HitDetail]]
    @raise ValueError: If the length of the scores and indices lists in search_results do not match.
    """
    pruned_hits = []

    for hit_scores, hit_indices in zip(search_results.total_scores, search_results.total_indices):
        if len(hit_scores) != len(hit_indices):
            raise ValueError(f"Length of scores and indices do not match. Got {len(hit_scores)} and {len(hit_indices)}")

        filtered_scores, filtered_sequence_tags, filtered_embeddings = get_filtered_annotations(
            hit_indices, hit_scores, threshold, discard_embeddings, ss
        )

        pruned_result = []
        for idx, (score, seq_id) in enumerate(zip(filtered_scores, filtered_sequence_tags)):
            embedding = [] if discard_embeddings else list(map(float, filtered_embeddings[idx]))
            pruned_result.append(HitDetail(HitID=seq_id, Score=score, Embedding=embedding))

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
    search_results, query_embeddings = request.app.state.ss.search(
        query_sequences, top_k=similarity_request.max_hits
    )  # type: BatchedSearchResults, np.ndarray

    pruned_hits = process_hits(
        search_results,
        similarity_request.threshold,
        similarity_request.discard_embeddings,
        request.app.state.ss,
    )

    proteins = []
    for i, query in enumerate(similarity_request.sequences):
        query_embedding = [] if similarity_request.discard_embeddings else list(map(float, query_embeddings[i]))
        proteins.append(
            QueryProtein(
                QueryId=query.id,
                Embedding=query_embedding,
                total_hits=len(pruned_hits[i]),
                Hits=pruned_hits[i],
            )
        )
    return SimilarityResponse(proteins=proteins)
