from pathlib import Path

from protein_search.embedders import get_embedder
from protein_search.search import SimilaritySearch


def setup_embeddings(model_name="esm2", pretrained_model_name_or_path="facebook/esm2_t6_8M_UR50D"):
    """
    Set up the embedder to use for similarity search
    This will get downloaded
    # /lus/eagle/projects/FoundEpidem/braceal/projects/kbase-protein-search/data/swiss-prot
    #
    # Faiss directory
    # Faiss.index
    # Subset of the data we will have on true production

    """

    # Initialize the embedder to use for similarity search
    return get_embedder(
        embedder_kwargs={
            # The name of the model architecture to use
            'name': model_name,
            # The model id to use for generating the embeddings
            # Looks like this downloads from the internet? #TODO Ask alex about this
            'pretrained_model_name_or_path': pretrained_model_name_or_path,
            # Use the model in half precision
            'half_precision': True,
            # Set the model to evaluation mode
            'eval_mode': True,
            # Compile the model for faster inference
            # Note: This can actually slow down the inference
            # if the number of queries is small
            'compile_model': False,
        },
    )


def setup_similarity_search(ss_dataset_dir="examples/examples/cath/cath_esm_8m_faiss"):
    embedder = setup_embeddings()
    return SimilaritySearch(dataset_dir=Path(ss_dataset_dir), embedder=embedder)


