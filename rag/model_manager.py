import requests
from langchain_ollama import OllamaEmbeddings, OllamaLLM

from default import DEFAULT_CONFIG as DC
from helper.config import load_config
from helper.file_record import Model
from helper.logger import log


class ModelManager:
    def __init__(self) -> None:
        load: dict[str, str] = load_config()
        llm = load.get("LANGUAGE_MODEL")
        em = load.get("EMBEDDING_MODEL")

        self.large_language_model = llm if llm else DC["LANGUAGE_MODEL"]
        self.embedding_model = em if em else DC["EMBEDDING_MODEL"]

    def getOllamaModelList(self):
        OLLAMA_URL = "http://localhost:11434"
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

        return result

    def getEmbedder(self):
        return OllamaEmbeddings(model=self.embedding_model)

    @log("Give a prompt to the LLM")
    def ask(self, input: str, temperature: float, num_ctx: int = 4096):
        return OllamaLLM(
            model=self.large_language_model, temperature=temperature, num_ctx=num_ctx
        ).invoke(input)
