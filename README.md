# Knower

A RAG that can help you study, by letting you get insights for you documents from your local knowledge base.

## Installation Method

To install Knower, clone this repository and install the required dependencies:

1st, clone the repository:

```bash
git clone https://github.com/theskpaul/Knower.git
```

2nd, install ollama and uv from your respective package manager if you are using Linux or,
     Visit [ollama.com](https://ollama.com) for Ollama and [docs.astral.sh/uv](https://docs.astral.sh/uv) for uv.

3rd, start ollam by:

```bash
ollama serve
```

3rd, fetch the model you want to use:

Example:
```bash
ollama pull hf.co/Qwen/Qwen3-Embedding-0.6B-GGUF:Q8_0
ollama pull hf.co/unsloth/gemma-4-E2B-it-qat-GGUF:UD-Q4_K_XL
```

4th, Navigate to the Knower directory and get respective packages using uv:

```bash
cd Knower
uv sync
```

5th, Finally start Knower by executing:

```bash
uv run src/main.py
```
