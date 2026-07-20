import os

import puremagic as magic
from file_record import Record


class FileManager:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.file_list = os.scandir(self.dir_path)

    def open_file(self, file) -> Record:
        try:
            matches = magic.magic_file(filename=file.path)
            mime = [matches[0][2], matches[0][3]]
        except Exception:
            mime = None

        return Record(
            name = file.name,
            content = '',
            metadata = {
                'mime': mime
            }
        )


    def getFiles(self):
        files = []
        for file in self.file_list:
            file_record = self.open_file(file)
            if not file_record.metadata['mime']:
                continue
            else:
                files.append(file_record)
        return files


if __name__ == "__main__":
    DATASET_PATH_NIX = "/home/var0/Projects/Knower/dataset"
    fm = FileManager(DATASET_PATH_NIX)

    for r in fm.getFiles():
        print(r)
