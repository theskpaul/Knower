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
ollama pull hf.co/CompendiumLabs/bge-base-en-v1.5-gguf
ollama pull hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF
```

4th, Navigate to the Knower directory and get respective packages using uv:

```bash
cd Knower
uv sync
```

5th, Finally start Knower by executing:

```bash
uv run main.py
```
