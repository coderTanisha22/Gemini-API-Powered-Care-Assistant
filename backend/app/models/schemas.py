from pydantic import BaseModel
from typing import List

class ActivityData(BaseModel):
    timestamps: List[str]
    activity_levels: List[int]

class AnomalyContext(BaseModel):
    anomaly_type: str
    expected_pattern: str
    observed_behavior: str
    severity: float
    confidence: float