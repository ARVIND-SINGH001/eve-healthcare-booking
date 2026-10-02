from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.payment import Payment, PaymentEvent


def _record_result(db: Session, booking: Booking, result: str, event_id: str) -> Payment:
    payment = db.scalar(select(Payment).where(Payment.booking_id == booking.id))
    if payment is None:
        payment = Payment(booking_id=booking.id, provider_event_id=event_id, status=result, amount=booking.amount)
        db.add(payment)
        db.flush()
    else:
        payment.provider_event_id = event_id
        payment.status = result
    booking.status = "CONFIRMED" if result == "SUCCESS" else "FAILED"
    db.commit()
    db.refresh(payment)
    return payment


def process_mock_payment(db: Session, booking_id: int, user_id: int, result: str) -> Payment:
    booking = db.get(Booking, booking_id)
    if booking is None or booking.user_id != user_id:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status == "CANCELLED":
        raise HTTPException(status_code=409, detail="Cancelled bookings cannot be paid")
    if db.scalar(select(Payment).where(Payment.booking_id == booking_id)):
        raise HTTPException(status_code=409, detail="A payment has already been recorded for this booking")
    return _record_result(db, booking, result, f"mock-{uuid4()}")


def process_webhook(db: Session, booking_id: int, event_id: str, result: str) -> tuple[Payment, bool]:
    # Keep all seen event IDs, so replaying an older event remains a no-op too.
    previous = db.scalar(select(PaymentEvent).where(PaymentEvent.provider_event_id == event_id))
    if previous is not None:
        return db.get(Payment, previous.payment_id), False
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status == "CANCELLED":
        raise HTTPException(status_code=409, detail="Cancelled bookings cannot be updated")
    payment = db.scalar(select(Payment).where(Payment.booking_id == booking_id))
    if payment is None:
        payment = Payment(booking_id=booking.id, provider_event_id=event_id, status=result, amount=booking.amount)
        db.add(payment)
        db.flush()
    else:
        payment.provider_event_id = event_id
        payment.status = result
    booking.status = "CONFIRMED" if result == "SUCCESS" else "FAILED"
    db.add(PaymentEvent(payment_id=payment.id, provider_event_id=event_id))
    db.commit()
    db.refresh(payment)
    return payment, True
