from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.centre_test import CentreTest


def create_booking(db: Session, user_id: int, centre_test_id: int, appointment_at: datetime) -> Booking:
    if appointment_at.tzinfo is None:
        raise HTTPException(status_code=422, detail="appointment_at must include a timezone")
    if appointment_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=422, detail="Appointment must be in the future")
    offering = db.scalar(select(CentreTest).where(CentreTest.id == centre_test_id))
    if offering is None:
        raise HTTPException(status_code=404, detail="Centre test offering not found")
    booking = Booking(user_id=user_id, centre_test_id=offering.id, appointment_at=appointment_at, amount=offering.price, status="PENDING")
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking
