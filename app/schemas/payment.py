from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MockPaymentRequest(BaseModel):
    booking_id: int = Field(gt=0)
    simulate_result: Literal["SUCCESS", "FAILED"]


class PaymentWebhookRequest(BaseModel):
    provider_event_id: str = Field(min_length=1, max_length=128)
    booking_id: int = Field(gt=0)
    status: Literal["SUCCESS", "FAILED"]


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    booking_id: int
    provider_event_id: str
    status: str
    amount: Decimal
