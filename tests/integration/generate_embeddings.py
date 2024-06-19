import numpy as np
import json
import os

from embedder import Esm2Embedder


def load_embedding_from_json(file_path):
    with open(file_path, "r") as f:
        embedding = json.load(f)
    return np.array(embedding)


def test_generate_embeddings():
    models = [
        ("facebook/esm2_t33_650M_UR50D", 1280, [
            ("MAQNRNSTGYA", 13),
            ("NLYIQWLKDGGPSSGRPPPS", 22)
        ]),
        ("facebook/esm2_t6_8M_UR50D", 320, [
            ("MAQNRNSTGYA", 13),
            ("NLYIQWLKDGGPSSGRPPPS", 22)
        ])
    ]

    # Full path to the directory containing expected embeddings
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

    for model_name, embed_dim, sequences in models:
        embedder = Esm2Embedder(model_name=model_name)
        for sequence, seq_len in sequences:
            embedding = embedder.embed([sequence])

            # Load the expected embedding from the JSON file
            file_path = os.path.join(base_path, f"{sequence}_{embed_dim}.json")
            expected_embedding = load_embedding_from_json(file_path)

            # Compare the generated embedding with the expected embedding
            assert embedding.shape == (1, seq_len, embed_dim), f"Expected shape (1, {seq_len}, {embed_dim}), but got {embedding.shape}"
            assert np.allclose(embedding.cpu().numpy(),
                               expected_embedding), f"Generated embedding does not match the saved embedding for {sequence} using {model_name}"

    print("All tests passed.")


# Run the test
test_generate_embeddings()
