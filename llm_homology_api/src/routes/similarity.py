from pprint import pprint

from fastapi import APIRouter, Request

from config import get_settings
from models.request_models import SimilarityRequest
from models.response_models import SimilarityResponse, QueryProtein , HitDetail

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

    ss = request.app.state.ss  # SimilaritySearch instance

    search_results, query_embeddings = ss.search(query_sequences, top_k=sr.max_hits)

    # BatchedSearchResults(total_scores=[
    #     [0.9999261498451233, 0.9999261498451233, 0.9999261498451233, 0.9999261498451233, 0.9999165534973145, 0.9999165534973145, 0.9999165534973145,
    #      0.9998984336853027, 0.9998682737350464, 0.9998661875724792],
    #     [0.9932831525802612, 0.9930819869041443, 0.9930461049079895, 0.9929633140563965, 0.9927730560302734, 0.992717981338501, 0.9927024245262146,
    #      0.9921532273292542, 0.9919975996017456, 0.9907838702201843]],
    #                      total_indices=[[387541, 126527, 126524, 126526, 126522, 126520, 126521, 387535, 387536, 126531],
    #                                     [301217, 301220, 127059, 281436, 214578, 214579, 127042, 127046, 214572, 281423]])

    pruned_hits = []
    total_hits = []
    for result in search_results:
        pruned_result = []
        for score, ind in zip(search_results.total_scores, search_results.total_indices):
            total_hits.append(len(ind))
            if score > threshold:
                # Get the sequence tags found by the search
                seq_id = ss.get_sequence_tags(ind)

                embedding = []
                if not discard_embeddings:
                    embedding = ss.get_sequence_embeddings(ind)
                    # Convert to python list for REST API
                    embedding = [float(i) for i in embedding[0].tolist()]
                pruned_result.append(HitDetail(HitID=seq_id, Score=score, Embedding=embedding))

        pruned_hits.append(pruned_result)

    proteins = []
    for i, protein in enumerate(query_sequences):

        qp = QueryProtein(
            QueryId=protein.id,
            Embedding=query_embeddings[i] if not discard_embeddings else [],
            total_hits=total_hits[i],
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
