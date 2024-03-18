from fastapi import APIRouter, Request

from config import get_settings
from models.request_models import SimilarityRequest
from models.response_models import SimilarityResponse, QueryProtein, HitDetail

router = APIRouter()
settings = get_settings()


def process_homologous_sequences(ss, result, threshold):
    homologous = {"total_hits": 0, "Hits": {}}
    for score, ind in zip(result.total_scores, result.total_indices):
        if score > threshold:
            seq_id = ss.get_sequence_tags(ind)
            embedding = ss.get_sequence_embeddings(ind)
            embedding_list = [float(i) for i in embedding[0].tolist()]
            homologous["Hits"][seq_id] = {"Score": score, "Embedding": embedding_list}
            homologous["total_hits"] += 1
    return homologous


def construct_query_protein(ss, query_index, query_embedding, result, threshold):
    query_seq_tag = ss.get_sequence_tags(query_index)
    query_embedding_list = [float(e) for e in query_embedding.tolist()]
    homologous = process_homologous_sequences(ss, result, threshold)
    return {
        "QueryId": query_seq_tag,
        "Embedding": query_embedding_list,
        "Homologous": homologous,
    }


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
        embedding = []
        if not discard_embeddings:
            embedding = ss.get_sequence_embeddings(ind)
            # Convert to python list for REST API
            embedding = [float(i) for i in embedding[ind].tolist()]
        pruned_result.append(HitDetail(HitID=seq_id[ind], Score=score[ind], Embedding=embedding))
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

    #     result = results[i]
    #
    #
    #     query_proteins.append({"QueryId": protein.id, "Embedding": query_embeddings[i] if not discard_embeddings else None,
    #                            "Homologous": {"total_hits": 0, "Hits": {}}})
    #
    # query_proteins = []
    #
    # # Combine each query embedding with its corresponding result into pairs
    # query_pairs = zip(query_embeddings, results)
    #
    # # Enumerate over these pairs to get both the index and the pair itself in each iteration
    # enumerated_pairs = enumerate(query_pairs)
    #
    # # Start the loop over these enumerated pairs
    # for query_index, pair in enumerated_pairs:
    #     # Unpack each pair into query_embedding and result
    #     query_embedding, result = pair
    #     query_protein = construct_query_protein(ss, query_index, query_embedding, result, threshold)
    #     query_proteins.append(query_protein)
    #
    # # for query_index, (query_embedding, result) in enumerate(zip(query_embeddings, results)):

    # return sr

#
# scores: [0.9999960660934448, 0.9999607801437378, 0.9981087446212769, 0.9968844056129456, 0.9927204847335815], indices: [467483, 322842, 322841, 322840, 467500], tags: ['Q5HAN0', 'Q5FFY2', 'Q2GHB1', 'Q3YRG6', 'Q0BLD5'], embeddings: (5, 1280)
# scores: [0.9999743700027466, 0.9885836243629456, 0.9855018854141235, 0.9789844751358032, 0.9772171974182129], indices: [467484, 436849, 142681, 520408, 467490], tags: ['Q5AYI7', 'P54967', 'O59778', 'Q11S94', 'A5FLT1'], embeddings: (5, 1280)