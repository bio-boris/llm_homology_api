from pathlib import Path

from protein_search.embedders import get_embedder
from protein_search.search import SimilaritySearch


def setup_embeddings(
    model_name="esm2",
    pretrained_model_name_or_path="facebook/esm2_t33_650M_UR50D",
    compile_model=None,
):
    if compile_model is None:
        raise ValueError("compile_model must be set to True or False")

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
            "name": model_name,
            # The model id to use for generating the embeddings
            # Looks like this downloads from the internet if its not available to local disk
            "pretrained_model_name_or_path": pretrained_model_name_or_path,
            # Use the model in half precision
            "half_precision": True,
            # Set the model to evaluation mode
            "eval_mode": True,
            # Compile the model for faster inference
            # Note: This can actually slow down the inference
            # if the number of queries is small
            "compile_model": compile_model,
        },
    )


def setup_similarity_search(ss_dataset_dir: str, embedder=None, compile_model=False):
    if embedder is None:
        embedder = setup_embeddings(compile_model=compile_model)
    return SimilaritySearch(dataset_dir=Path(ss_dataset_dir), embedder=embedder)
