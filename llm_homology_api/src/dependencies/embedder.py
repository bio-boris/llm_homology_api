import torch
from transformers import EsmForMaskedLM, EsmTokenizer


class Esm2Embedder:
    """Embedder for the ESM-2 model"""

    def __init__(self, model_name='facebook/esm2_t6_8M_UR50D', half_precision: bool = True, eval_mode: bool = True, device: str = None):
        tokenizer = EsmTokenizer.from_pretrained(model_name)
        model = EsmForMaskedLM.from_pretrained(model_name)
        model.eval() if eval_mode else model.train()
        model.half() if half_precision else model.float()
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        device = torch.device(device)
        model.to(device)
        self.tokenizer = tokenizer
        self.model = model
        self.device = device

    def embed(self, sequences):
        """Embed protein sequences using the ESM-2 model."""
        # Tokenize the sequences, ensuring tensors are on the same device as the model
        batch_encoding = self.tokenizer(sequences, return_tensors='pt', padding=True, truncation=True)
        batch_encoding = {k: v.to(self.device) for k, v in batch_encoding.items()}

        # Perform inference without computing gradients
        with torch.no_grad():
            outputs = self.model(**batch_encoding, output_hidden_states=True)

        return outputs.hidden_states[-1]


# Example usage:
embedder = Esm2Embedder()
sequences = ["Protein sequence 1", "Protein sequence 2"]
embeddings = embedder.embed(sequences)
print(embeddings.shape)
