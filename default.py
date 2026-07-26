from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

PATH = {
    "config": BASE_DIR / "config",
    "temp_config": BASE_DIR / "data" / "config",
    "chat_history": BASE_DIR / "data",
    "sources": BASE_DIR / "data" / "sources",
    "vectordb": BASE_DIR / "data" / "vectordb",
    "log": BASE_DIR / "data" / "log",
    "cross_encoder": BASE_DIR / "Models" / "cross_encoder",
}

DEFAULT_CONFIG = {
    "LANGUAGE_MODEL": "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest",
    "EMBEDDING_MODEL": "hf.co/CompendiumLabs/bge-base-en-v1.5-gguf:latest",
}


def check_and_make():
    for p in PATH.values():
        p.mkdir(parents=True, exist_ok=True)
