import json
from dataclasses import asdict, dataclass, field

from langchain_core.documents import Document


@dataclass
class Record:
    name: str
    content: str
    metadata: dict = field(default_factory=dict)

    def __str__(self):
        return self.to_json()

    def to_json(self, **kwargs):
        return json.dumps(asdict(self), **kwargs)

    def to_document(self):
        return Document(
            page_content=self.content, metadata={**self.metadata, "source": self.name}
        )
