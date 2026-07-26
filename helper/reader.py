import pymupdf4llm

from helper.logger import log as l


@l("Read PDF")
def read_pdf(path: str) -> str:
    md: str = pymupdf4llm.to_markdown(path).__str__()
    return md


@l("Read TXT")
def read_txt(path: str) -> str:
    with open(file=path, mode="r", encoding="utf-8") as f:
        return f.read()


READER = {"application/pdf": read_pdf, "text/plain": read_txt}


@l("Select function based on the file type")
def read(mime: str, path: str):
    reader = READER.get(mime)
    return reader(path) if reader else ""
