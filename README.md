# LLM Homology API
* A fastapi

# Install with a local .venv
```
Ensure you poetry has the following
```
poetry config virtualenvs.in-project true
poetry config virtualenvs.create true
```
Then run
```
poetry install
```
# Updating Dependencies
```
poetry add uvicorn
poetry add pytest --dev
```

# ESM-2: 

This is a state-of-the-art general-purpose protein language model
that can be used to predict various protein properties directly from
individual sequences. Given its broad capabilities and strong performance in predicting
both structure and function from sequences,
ESM-2 models (e.g., esm2_t36_3B_UR50D or esm2_t48_15B_UR50D) would be highly effective if your goal includes a comprehensive analysis that extends beyond mere sequence similarity to include functional or structural predictions.


Use Case: For rapid prototyping or when working with limited resources, smaller models like esm2_t6_8M_UR50D or esm2_t12_35M_UR50D could be more appropriate. For extensive research or industrial applications where high accuracy is crucial, larger models like esm2_t48_15B_UR50D may be more suitable.

