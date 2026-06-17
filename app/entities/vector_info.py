from dataclasses import dataclass


@dataclass
class VectorInfo:
    id: str
    embeding_text: str
    metadata: dict[str, any]
