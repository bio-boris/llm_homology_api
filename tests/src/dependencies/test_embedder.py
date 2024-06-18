from unittest.mock import MagicMock, patch

import pytest
import torch
from src.dependencies.embedder import Esm2Embedder


@pytest.fixture
def mock_torch(mocker):
    mocker.patch('torch.cuda.is_available', return_value=True)
    mocker.patch('torch.device', return_value='cuda')


@pytest.fixture
def embedder(mock_torch, model_name, half_precision, eval_mode, device):
    with patch('transformers.EsmTokenizer.from_pretrained', return_value=MagicMock()) as mock_tokenizer, \
            patch('transformers.EsmForMaskedLM.from_pretrained', return_value=MagicMock(spec=torch.nn.Module)) as mock_model:
        embedder = Esm2Embedder(model_name=model_name, half_precision=half_precision, eval_mode=eval_mode, device=device)
    return embedder


@pytest.mark.parametrize("model_name, half_precision, eval_mode, device", [
    ('facebook/esm2_t6_8M_UR50D', True, True, 'cuda'),
    ('facebook/esm2_t6_8M_UR50D', False, True, 'cuda'),
    ('facebook/esm2_t6_8M_UR50D', True, False, 'cpu'),
    ('facebook/esm2_t6_8M_UR50D', False, False, 'cpu')
])
def test_initialization(embedder):
    assert isinstance(embedder.model, torch.nn.Module), "Model should be an instance of torch.nn.Module"
    expected_device = 'cuda' if torch.cuda.is_available() else 'cpu'
    assert str(embedder.device) == expected_device, f"Device should be set to '{expected_device}'"


@pytest.mark.parametrize("model_name, half_precision, eval_mode", [
    ('facebook/esm2_t6_8M_UR50D', True, True),
    ('facebook/esm2_t6_8M_UR50D', False, True),
    ('facebook/esm2_t6_8M_UR50D', True, False),
    ('facebook/esm2_t6_8M_UR50D', False, False)
])
def test_embedder_initialization(model_name, half_precision, eval_mode):
    embedder = Esm2Embedder(model_name=model_name, half_precision=half_precision, eval_mode=eval_mode, device='cuda')

    assert embedder.model is not None, "Model should be initialized"
    assert embedder.tokenizer is not None, "Tokenizer should be initialized"
    assert embedder.device is not None, "Device should be set"
    assert embedder.device == torch.device('cuda'), "Device should be CUDA"

    assert embedder.model.training == (not eval_mode), f"Model training mode should be {not eval_mode}"
    expected_dtype = torch.float16 if half_precision else torch.float32
    assert embedder.model.dtype == expected_dtype, f"Model dtype should be {expected_dtype}"


