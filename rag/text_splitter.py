import hashlib

from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker

from rag.helper.logger import log
from rag.helper.file_record import Record


class TextSplitter:
    def __init__(self, datasets: list[Record]):
        self.datasets = datasets

    @log("Split Dataset")
    def split_dataset(
        self,
        embedding_function,
    ) -> list[Document]:
        splits: list[Document] = []

        for data in self.datasets:
            docs = [
                data.to_document()
            ]

            splitter = SemanticChunker(
                embeddings=embedding_function,
                add_start_index=True,
            )

            for chunk_count, chunk in enumerate(splitter.split_documents(docs)):
                if not chunk.page_content.strip():
                    continue
                splits.append(
                    Document(
                        metadata={
                            "source": chunk.metadata["source"],
                            "chunk_count": chunk_count,
                            "start_index": chunk.metadata["start_index"],
                            "file_sha256": chunk.metadata["file_sha256"],
                            "chunk_sha256": hashlib.sha256(
                                chunk.page_content.encode()
                            ).hexdigest(),
                        },
                        page_content=chunk.page_content,
                    )
                )

        return splits
