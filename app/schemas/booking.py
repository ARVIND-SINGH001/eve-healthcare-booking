from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BookingCreate(BaseModel):
    centre_test_id: int = Field(gt=0)
    appointment_at: datetime


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    centre_test_id: int
    appointment_at: datetime
    amount: Decimal
    status: str
    created_at: datetime
