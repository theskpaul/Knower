from dataclasses import dataclass, field

from langchain_ollama import OllamaEmbeddings, OllamaLLM

from logger import log as l


@dataclass
class Model:
    name: str
    model: str
    size: int
    capabilities: list
    details: dict = field(default_factory=dict)


@l("Get ollama model list")
def getOllamaModelList():
    import requests

    OLLAMA_URL = "http://localhost:11434"
    try:
        req = requests.get(OLLAMA_URL + "/api/tags")
        output = req.json()

        result = []

        for item in output["models"]:
            result.append(
                Model(
                    name=item["name"],
                    model=item["model"],
                    size=item["size"],
                    capabilities=item["capabilities"],
                    details=item["details"],
                )
            )
    except requests.exceptions.RequestException:
        result = []

    return result


class ModelManager:
    def __init__(
        self,
        language_model: str,
        embedding_model: str,
    ) -> None:
        self.large_language_model = language_model
        self.embedding_model = embedding_model

    @l("Get embedding function")
    def getEmbedder(self):
        return OllamaEmbeddings(model=self.embedding_model)

    @l("Give a prompt to the LLM")
    def ask(self, input: str, temperature: float, num_ctx: int = 4096):
        return OllamaLLM(
            model=self.large_language_model, temperature=temperature, num_ctx=num_ctx
        ).invoke(input)
