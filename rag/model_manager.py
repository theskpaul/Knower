from langchain_ollama import OllamaEmbeddings, OllamaLLM

from rag.utils.logger import log


class ModelManager:
    def __init__(self, llm="", embedding_model="") -> None:
        self.large_language_model = llm
        self.embedding_model = embedding_model

    @log("Give a prompt to the LLM")
    def ask(self, input: str, temperature: float):
        OllamaLLM(model=self.large_language_model, temperature=temperature).invoke(
            input
        )

    def getEmbedder(self):
        return OllamaEmbeddings(model=self.embedding_model)
