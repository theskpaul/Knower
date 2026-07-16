import platform

from langchain_chroma import Chroma
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

PERSISTENT_DIR_NIX = "./vectordb"
PERSISTENT_DIR_WINDOWS = ".\\vectordb"


class VectorStore:
    def __init__(self, embedding_function):
        if platform.system() == "Linux":
            self.persist_directory = PERSISTENT_DIR_NIX
        elif platform.system() == "Windows":
            self.persist_directory = PERSISTENT_DIR_WINDOWS
        self.embedding_function = embedding_function
        self.__vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=embedding_function,
        )

    def store(self, document_list: list[Document]):
        self.__vector_store.add_documents(document_list)

    def search(self, search_query: str, number_of_top_results: int) -> list[Document]:
        return self.__vector_store.similarity_search(
            query=search_query, k=number_of_top_results
        )

    def rerank(
        self,
        search_query: str,
        number_of_top_results: int,
        number_of_fetched_results: int,
        model: str,
    ):
        reranker = CrossEncoder(model)
        retrieved_docs = self.search(search_query, number_of_fetched_results)
        pairs = [(search_query, doc.page_content) for doc in retrieved_docs]
        scores = reranker.predict(pairs)
        results = list(zip(scores, retrieved_docs))
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:number_of_top_results]
