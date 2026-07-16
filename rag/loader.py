import hashlib
import os
import platform

import pymupdf4llm

DATASET_PATH_NIX = "./dataset"
DATASET_PATH_WINDOWS = ".\\dataset"


class load_dataset:
    def __init__(self):
        if platform.system() == "Linux":
            self.path = DATASET_PATH_NIX
            self.__file_list = os.scandir(self.path)
        elif platform.system() == "Windows":
            self.path = DATASET_PATH_WINDOWS
            self.__file_list = os.scandir(self.path)

    def load_pdf(self, file):
        return pymupdf4llm.to_markdown(file.path, page_chunks=True)

    def generate_sha256(self, file) -> str:
        with open(file.path, "rb") as f:
            hash_func = hashlib.new("sha256")
            while chunk := f.read(8192):
                hash_func.update(chunk)

        return hash_func.hexdigest()

    def contents(self) -> list[dict]:
        dataset: list = []

        for f in self.__file_list:
            sha256 = self.generate_sha256(f)

            with open(f.path, "r", encoding="utf-8") as file:
                content = file.read().rstrip()
                dataset.append(
                    {
                        "metadata": {
                            "source": f.name,
                            "sha256": sha256,
                        },
                        "content": content,
                    }
                )

        return dataset
