import json
from dataclasses import asdict, dataclass, field


@dataclass
class Record:
    name: str
    content: str
    metadata: dict = field(default_factory=dict)

    def __str__(self):
        return self.to_json()

    def to_json(self, **kwargs):
        return json.dumps(asdict(self), **kwargs)
