import os
import hashlib

import puremagic as magic
from helper.file_record import Record
from helper.reader import read
from helper.logger import log

class FileManager:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.file_list = os.scandir(self.dir_path)

    @log("Compute SHA256")
    def compute_sha256(self, path) -> str:
        with open(path, mode='rb') as byte_stream:
            hash = hashlib.new(name='sha256')
            while chunk:= byte_stream.read(8192):
                hash.update(chunk)
            return hash.hexdigest()

    @log("Open file")
    def open_file(self, file) -> Record:
        try:
            matches = magic.magic_file(filename=file.path)
            extension = matches[0][2]
            mime = matches[0][3]
            metadata = {
                'file_extension': extension,
                'mime': mime,
                'file_sha256': self.compute_sha256(file.path)
            }

        except Exception:
            mime = None
            metadata = {
                'mime': mime
            }

        content = read(mime=mime, path=file.path) if mime else ''

        return Record(
            name = file.name,
            content = content,
            metadata = metadata
        )

    @log("Collection of Files")
    def get_file_records(self):
        files = []
        for file in self.file_list:
            file_record = self.open_file(file)
            if not file_record.metadata['mime']:
                continue
            else:
                files.append(file_record)
        return files
