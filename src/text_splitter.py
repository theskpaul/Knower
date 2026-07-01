import hashlib

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextSplitter:
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.__chunk_size = chunk_size
        self.__chunk_overlap = chunk_overlap

    def split_dataset(self, datasets: list[dict]) -> list[Document]:
        splits: list[Document] = []

        for data in datasets:
            docs = [
                Document(
                    metadata={
                        "source": data["metadata"]["source"],
                        "file_sha256": data["metadata"]["sha256"],
                    },
                    page_content=data["content"],
                )
            ]

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.__chunk_size,
                chunk_overlap=self.__chunk_overlap,
                add_start_index=True,
            )

            for chunk_count, chunk in enumerate(splitter.split_documents(docs)):
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


# Test
# if __name__ == "__main__":
#     DATASET_PATH: str = "./dataset"

#     ts = TextSplitter(500, 20)
#     from loader import load_dataset as ld

#     dataset = ld(DATASET_PATH)
#     docs = ts.split_dataset(dataset.contents())

#     for data in docs:
#         print(
#             f"""# Chunk_{data.metadata["chunk_count"] + 1}
# metadata:[
#     "source": {data.metadata["source"]},
#     "file_sha256": {data.metadata["file_sha256"]},
#     "chunk_sha256": {data.metadata["chunk_sha256"]}
# ],
# Page_content: {data.page_content}
#             """
#         )
