from pprint import pprint

import protein_search.search
from fastapi import APIRouter, Request

from config import get_settings
from models.request_models import SimilarityRequest
from models.response_models import SimilarityResponse, QueryProtein, HitDetail

router = APIRouter()
settings = get_settings()


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
    @param discard_embeddings: Boolean value to determine whether to discard the embeddings of the queries and hits.
    @param ss: SimilaritySearch object used for searching.
    @return: A list of pruned hits for each query sequence.
    @rtype: list[list[HitDetail]]
    @raise ValueError: If the length of the scores and indices lists in search_results do not match.
    """

    pruned_hits = []
    for scores, indices in zip(search_results.total_scores, search_results.total_indices):

        if len(scores) != len(indices):
            raise ValueError(f"Length of scores ({len(scores)}) and indices ({len(indices)}) do not match.")

        sequence_tags = ss.get_sequence_tags(indices)
        pruned_result = []
        for idx, (seq_id, score) in enumerate(zip(sequence_tags, scores)):
            if score >= threshold:
                embedding = []
                if not discard_embeddings:
                    # get_sequence_embeddings will return shape (1, EmbeddingDim).
                    embeddings_raw = ss.get_sequence_embeddings(indices)[0].tolist()
                    embedding = [list(map(float, e)) for e in embeddings_raw]
                pruned_result.append(HitDetail(HitID=seq_id, Score=score, Embedding=embedding))
        # Unprocessible entity troubelshooting
        print(pruned_result)

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
    pruned_hits = process_hits(
        search_results,
        similarity_request.threshold,
        similarity_request.discard_embeddings,
        request.app.state.ss,
    )
    proteins = []
    for i, query in enumerate(similarity_request.sequences):
        query_embedding = []
        if not similarity_request.discard_embeddings:
            query_embedding = [list(map(float, e)) for e in query_embeddings[i]]
        proteins.append(
            QueryProtein(
                QueryId=query.id,
                Embedding=query_embedding,
                total_hits=1,
                Hits=pruned_hits[i],
            )
        )
    pprint(SimilarityResponse(proteins=proteins))
    return SimilarityResponse(proteins=proteins)
