import os
import time
from abc import ABC, abstractmethod

from datasets import tqdm

start_time = time.time()
import faiss
import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import EsmForMaskedLM, EsmTokenizer, PreTrainedTokenizer, BatchEncoding

end_time = time.time()
print(f"Imports took {end_time - start_time} seconds")


class InMemoryDataset(Dataset):
    """Holds the data in memory for efficient batching."""

    def __init__(self, data: list[str]) -> None:
        self.data = data

    def __len__(self) -> int:
        """Length of the dataset."""
        return len(self.data)

    def __getitem__(self, idx: int) -> str:
        """Get an item from the dataset."""
        return self.data[idx]


class DataCollator:
    """Data collator for batching sequences.
    Todo ask alex why we cant use

    from transformers import DataCollatorWithPadding
    data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)

    """

    def __init__(self, tokenizer: PreTrainedTokenizer, max_length: int = 1280) -> None:
        """Initialize the data collator."""
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __call__(self, batch: list[str]) -> BatchEncoding:
        """Collate the batch of sequences."""
        return self.tokenizer(
            batch,
            padding=True,
            truncation=True,
            return_tensors='pt',
            max_length=self.max_length,
        )


class Esm2EmbedderBase(ABC):
    """Embedder for the ESM-2 model"""

    def __init__(self, local_model_dir='local_models', model_name='facebook/esm2_t33_650M_UR50D', half_precision: bool = True, eval_mode: bool = True,
                 metric: str = 'inner_product', compile_model=True):
        """
        Initialize the ESM-2 embedder.

        """
        compile_model = False  # Debugging

        self.local_model_dir = local_model_dir
        self.model_name = model_name
        self.half_precision = half_precision
        self.eval_mode = eval_mode
        self.metric = metric

        model_cache_dir = os.path.join(local_model_dir, f"models--{model_name.replace('/', '--')}")
        snapshot_exists = self.check_snapshot_exists(model_cache_dir)

        model_source = model_cache_dir if snapshot_exists else model_name

        tokenizer = EsmTokenizer.from_pretrained(model_source, cache_dir=local_model_dir)
        model = EsmForMaskedLM.from_pretrained(model_source, cache_dir=local_model_dir)

        if not snapshot_exists:
            self.save_model_locally(model, tokenizer, model_cache_dir)

        if eval_mode:
            model.eval()
        if half_precision:
            model.half()

        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        device = torch.device(device)
        model.to(device)

        if compile_model:
            model = torch.compile(model, fullgraph=True)

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

    def average_pool(
            self,
            embeddings: torch.Tensor,
            attention_mask: torch.Tensor,
    ) -> torch.Tensor:
        """Average pool the hidden states using the attention mask.

        Parameters
        ----------
        embeddings : torch.Tensor
            The hidden states to pool (B, SeqLen, HiddenDim).
        attention_mask : torch.Tensor
            The attention mask for the hidden states (B, SeqLen).

        Returns
        -------
        torch.Tensor
            The pooled embeddings (B, HiddenDim).
        """
        # Get the sequence lengths
        seq_lengths = attention_mask.sum(axis=1)

        # Set the attention mask to 0 for start and end tokens
        attention_mask[:, 0] = 0
        attention_mask[:, seq_lengths - 1] = 0

        # Create a mask for the pooling operation (B, SeqLen, HiddenDim)
        pool_mask = attention_mask.unsqueeze(-1).expand(embeddings.shape)

        # Sum the embeddings over the sequence length (use the mask to avoid
        # pad, start, and stop tokens)
        sum_embeds = torch.sum(embeddings * pool_mask, 1)

        # Avoid division by zero for zero length sequences by clamping
        sum_mask = torch.clamp(pool_mask.sum(1), min=1e-9)

        # Compute mean pooled embeddings for each sequence
        return sum_embeds / sum_mask

    @abstractmethod
    def get_pooled_embeddings(self, sequences: list[str]):
        """
        Abstract method to get the pooled embeddings for a list of sequences.
        """
        pass


class ESM2EmbedderSerial(Esm2EmbedderBase):

    @torch.no_grad()
    def get_pooled_embeddings(self, sequences: list[str], max_length=1280) -> np.ndarray:
        # Tokenize the query sequences
        batch_encoding = self.tokenizer(
            sequences,
            padding=True,
            truncation=True,
            return_tensors='pt',
            max_length=max_length
        )

        # Move the batch encoding to the device
        inputs = batch_encoding.to(self.device)

        # Embed the query sequences
        query_embeddings = self.model(**batch_encoding, output_hidden_states=True).hidden_states[-1]

        # Compute average embeddings for the query sequences
        pool_embeds = self.average_pool(query_embeddings, inputs.attention_mask)

        # Convert the query embeddings to numpy float32 for FAISS
        pool_embeds = pool_embeds.cpu().numpy().astype(np.float32)

        # Normalize the embeddings for inner product search
        if self.metric == 'inner_product':
            faiss.normalize_L2(pool_embeds)

        return pool_embeds


class ESM2EmbedderBatch(Esm2EmbedderBase):

    @torch.no_grad()
    def get_pooled_embeddings(self, sequences: list[str], batch_size: int = 8, num_workers: int = 4, prefetch_factor=2,
                              max_length=1280) -> np.ndarray:
        # Build a torch dataset for efficient batching
        dataloader = DataLoader(
            dataset=InMemoryDataset(sequences),
            batch_size=batch_size,
            num_workers=num_workers,
            prefetch_factor=prefetch_factor,
            pin_memory=True,
            collate_fn=DataCollator(self.tokenizer),
        )

        # Get the number of embeddings and the embedding size
        num_embeddings = len(dataloader.dataset)
        embedding_size = self.model.config.hidden_size

        # Initialize a torch tensor for storing embeddings in host memory
        all_embeddings = torch.empty(
            (num_embeddings, embedding_size),
            dtype=torch.float32,
        )

        # logger.info(f"Total number of sequences: {num_embeddings}")
        # logger.info(f"Embedding size: {embedding_size}")

        # Index for storing embeddings
        idx = 0

        for batch_num, batch in enumerate(dataloader, start=1):
            # logger.info(f"Processing batch {batch_num}/{len(dataloader)}")

            # Ensure batch is a list of strings
            batch = [sequence for sequence in batch]

            # Tokenize the batch with max_length
            inputs = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                return_tensors='pt',
                max_length=max_length
            )

            # Move the batch to the model device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Get the model outputs with a forward pass
            outputs = self.model(**inputs, output_hidden_states=True).hidden_states[-1]

            # Compute the average pooled embeddings
            pooled_embeds = self.average_pool(outputs, inputs['attention_mask'])

            # Get the batch size
            batch_size = inputs['input_ids'].shape[0]

            # Store the pooled embeddings in the output buffer
            # all_embeddings[idx:idx + batch_size, :] = pooled_embeds.cpu()

#            Handle the case where batch size is 1
            if batch_size == 1:
                all_embeddings[idx:idx + 1, :] = pooled_embeds.cpu().unsqueeze(0)
            else:
                # Store the pooled embeddings in the output buffer
                all_embeddings[idx:idx + batch_size, :] = pooled_embeds.cpu()

            # Increment the output buffer index by the batch size
            idx += batch_size

        # logger.info("All batches processed")

        # Convert to numpy float32 for FAISS
        all_embeddings = all_embeddings.numpy().astype(np.float32)

        # Normalize the embeddings for inner product search if needed
        if self.metric == 'inner_product':
            faiss.normalize_L2(all_embeddings)

        # logger.info("Embedding normalization completed")

        return all_embeddings
