import os
import torch
from transformers import EsmForMaskedLM, EsmTokenizer

class Esm2Embedder:
    """Embedder for the ESM-2 model"""

    def __init__(self, local_model_dir='local_models', model_name='facebook/esm2_t33_650M_UR50D', half_precision: bool = True, eval_mode: bool = True, device: str = None):
        self.local_model_dir = local_model_dir
        self.model_name = model_name
        self.half_precision = half_precision
        self.eval_mode = eval_mode

        model_cache_dir = os.path.join(local_model_dir, f"models--{model_name.replace('/', '--')}")
        snapshot_exists = self.check_snapshot_exists(model_cache_dir)

        model_source = model_cache_dir if snapshot_exists else model_name

        tokenizer = EsmTokenizer.from_pretrained(model_source, cache_dir=local_model_dir)
        model = EsmForMaskedLM.from_pretrained(model_source, cache_dir=local_model_dir)

        if not snapshot_exists:
            self.save_model_locally(model, tokenizer, model_cache_dir)

        model.eval() if eval_mode else model.train()
        model.half() if half_precision else model.float()

        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        device = torch.device(device)
        model.to(device)

        self.tokenizer = tokenizer
        self.model = model
        self.device = device

    def check_snapshot_exists(self, model_cache_dir):
        snapshot_dir = os.path.join(model_cache_dir, "snapshots")
        if os.path.exists(snapshot_dir):
            for subdir in os.listdir(snapshot_dir):
                subdir_path = os.path.join(snapshot_dir, subdir)
                if os.path.isdir(subdir_path):
                    model_files = ["config.json", "model.safetensors", "tokenizer_config.json", "vocab.txt", "special_tokens_map.json"]
                    if all(os.path.exists(os.path.join(subdir_path, file)) for file in model_files):
                        return True
        return False

    def save_model_locally(self, model, tokenizer, model_cache_dir):
        os.makedirs(model_cache_dir, exist_ok=True)
        model.save_pretrained(model_cache_dir)
        tokenizer.save_pretrained(model_cache_dir)

    def embed(self, sequences):
        """Embed protein sequences using the ESM-2 model."""
        batch_encoding = self.tokenizer(sequences, return_tensors='pt', padding=True, truncation=True)
        batch_encoding = {k: v.to(self.device) for k, v in batch_encoding.items()}

        with torch.no_grad():
            outputs = self.model(**batch_encoding, output_hidden_states=True)

        return outputs.hidden_states[-1]
