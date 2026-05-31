from typing import Literal, List

from pydantic import BaseModel

LLM_FEELING = Literal["positive", "negative", "neutral"]


class LLMAdapterResult(BaseModel):
    feeling: LLM_FEELING
    topics: List[str]
    summary: str
    latency: float
    tokens: int
    cost: float
