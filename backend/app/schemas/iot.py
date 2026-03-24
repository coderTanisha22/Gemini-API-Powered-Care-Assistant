from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class IoTData(BaseModel):
    user_id: str
    timestamp: datetime
    sensor_type: str
    activity_label: Optional[str]
    value: Optional[float]
    confidence: Optional[float]