from fastapi import APIRouter

from app.api.dependencies import CurrentUser, DbSession
from app.schemas.payment import MockPaymentRequest, PaymentResponse, PaymentWebhookRequest
from app.services.payment_service import process_mock_payment, process_webhook


router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", response_model=PaymentResponse, status_code=201)
def create_mock_payment(payload: MockPaymentRequest, db: DbSession, user: CurrentUser):
    return process_mock_payment(db, payload.booking_id, user.id, payload.simulate_result)


@router.post("/webhook")
def payment_webhook(payload: PaymentWebhookRequest, db: DbSession):
    payment, processed = process_webhook(db, payload.booking_id, payload.provider_event_id, payload.status)
    if not processed:
        return {"message": "Event already processed", "payment_id": payment.id}
    return {
        "message": "Event processed",
        "payment_id": payment.id,
        "payment_status": payment.status,
        "booking_status": "CONFIRMED" if payment.status == "SUCCESS" else "FAILED",
    }


