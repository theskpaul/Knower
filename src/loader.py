import hashlib
import os


class load_dataset:
    def __init__(self, path):
        self.path = path
        self.__file_list = os.scandir(self.path)

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
