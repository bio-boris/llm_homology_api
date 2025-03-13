# import os
#
# import faiss
# import numpy as np
# import torch
# from torch.utils.data import DataLoader, Dataset
# from transformers import EsmForMaskedLM, EsmTokenizer, DataCollator
#
#
# class Esm2Embedder:
#     """Embedder for the ESM-2 model"""
#
#     def __init__(self, local_model_dir='local_models', model_name='facebook/esm2_t33_650M_UR50D', half_precision: bool = True, eval_mode: bool = True,
#                  metric: str = 'inner_product', compile_model=False, ):
#         """
#         Initialize the ESM-2 embedder.
#
#         """
#         self.local_model_dir = local_model_dir
#         self.model_name = model_name
#         self.half_precision = half_precision
#         self.eval_mode = eval_mode
#         self.metric = metric
#
#         model_cache_dir = os.path.join(local_model_dir, f"models--{model_name.replace('/', '--')}")
#         snapshot_exists = self.check_snapshot_exists(model_cache_dir)
#
#         model_source = model_cache_dir if snapshot_exists else model_name
#
#         tokenizer = EsmTokenizer.from_pretrained(model_source, cache_dir=local_model_dir)
#         model = EsmForMaskedLM.from_pretrained(model_source, cache_dir=local_model_dir)
#
#         if not snapshot_exists:
#             self.save_model_locally(model, tokenizer, model_cache_dir)
#
#         if eval_mode:
#             model.eval()
#         if half_precision:
#             model.half()
#
#         device = 'cuda' if torch.cuda.is_available() else 'cpu'
#         device = torch.device(device)
#         model.to(device)
#
#         if compile_model:
#             model = torch.compile(model, fullgraph=True)
#
#         self.tokenizer = tokenizer
#         self.model = model
#         self.device = device
#
#     def check_snapshot_exists(self, model_cache_dir):
#         snapshot_dir = os.path.join(model_cache_dir, "snapshots")
#         if os.path.exists(snapshot_dir):
#             for subdir in os.listdir(snapshot_dir):
#                 subdir_path = os.path.join(snapshot_dir, subdir)
#                 if os.path.isdir(subdir_path):
#                     model_files = ["config.json", "model.safetensors", "tokenizer_config.json", "vocab.txt", "special_tokens_map.json"]
#                     if all(os.path.exists(os.path.join(subdir_path, file)) for file in model_files):
#                         return True
#         return False
#
#     def save_model_locally(self, model, tokenizer, model_cache_dir):
#         os.makedirs(model_cache_dir, exist_ok=True)
#         model.save_pretrained(model_cache_dir)
#         tokenizer.save_pretrained(model_cache_dir)
#
#     def average_pool(
#             self,
#             embeddings: torch.Tensor,
#             attention_mask: torch.Tensor,
#     ) -> torch.Tensor:
#         """Average pool the hidden states using the attention mask.
#
#         Parameters
#         ----------
#         embeddings : torch.Tensor
#             The hidden states to pool (B, SeqLen, HiddenDim).
#         attention_mask : torch.Tensor
#             The attention mask for the hidden states (B, SeqLen).
#
#         Returns
#         -------
#         torch.Tensor
#             The pooled embeddings (B, HiddenDim).
#         """
#         # Get the sequence lengths
#         seq_lengths = attention_mask.sum(axis=1)
#
#         # Set the attention mask to 0 for start and end tokens
#         attention_mask[:, 0] = 0
#         attention_mask[:, seq_lengths - 1] = 0
#
#         # Create a mask for the pooling operation (B, SeqLen, HiddenDim)
#         pool_mask = attention_mask.unsqueeze(-1).expand(embeddings.shape)
#
#         # Sum the embeddings over the sequence length (use the mask to avoid
#         # pad, start, and stop tokens)
#         sum_embeds = torch.sum(embeddings * pool_mask, 1)
#
#         # Avoid division by zero for zero length sequences by clamping
#         sum_mask = torch.clamp(pool_mask.sum(1), min=1e-9)
#
#         # Compute mean pooled embeddings for each sequence
#         return sum_embeds / sum_mask
#
#     @torch.no_grad()
#     def get_pooled_embeddings(self, sequences: list[str]):
#
#
# class InMemoryDataset(Dataset):
#     """Holds the data in memory for efficient batching."""
#
#     def __init__(self, data: list[str]) -> None:
#         self.data = data
#
#     def __len__(self) -> int:
#         """Length of the dataset."""
#         return len(self.data)
#
#     def __getitem__(self, idx: int) -> str:
#         """Get an item from the dataset."""
#         return self.data[idx]