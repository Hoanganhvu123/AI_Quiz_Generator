from pydantic import BaseModel
from typing import Dict

class Question(BaseModel):
    question: str
    options: Dict[str, str]
    correct_answer: str
    explanation: str = ""

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)