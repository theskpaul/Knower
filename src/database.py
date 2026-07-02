from langchain_chroma import Chroma
from langchain_core.documents import Document


class VectorStore:
    def __init__(self, database_loaction, embedding_function):
        self.database_location = database_loaction
        self.embedding_function = embedding_function
        self.__vector_store = Chroma(
            persist_directory=database_loaction, embedding_function=embedding_function
        )

    def store(self, document_list: list[Document]):
        self.__vector_store.add_documents(document_list)

    def search(self, search_query: str, number_of_top_results: int) -> list[Document]:
        return self.__vector_store.similarity_search(
            query=search_query, k=number_of_top_results
        )
