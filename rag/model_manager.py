from langchain_ollama import OllamaEmbeddings, OllamaLLM

from rag.helper.logger import log


class ModelManager:
    def __init__(self, llm="", embedding_model="") -> None:
        self.large_language_model = llm
        self.embedding_model = embedding_model

    @log("Give a prompt to the LLM")
    def ask(self, input: str, temperature: float, num_ctx:int = 4096):
        return OllamaLLM(
            model=self.large_language_model, temperature=temperature, num_ctx=num_ctx
        ).invoke(input)

    def getEmbedder(self):
        return OllamaEmbeddings(model=self.embedding_model)
