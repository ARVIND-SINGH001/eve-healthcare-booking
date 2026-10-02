from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.dependencies import CurrentUser, DbSession
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import create_booking


router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingResponse, status_code=201)
def create_user_booking(payload: BookingCreate, db: DbSession, user: CurrentUser):
    return create_booking(db, user.id, payload.centre_test_id, payload.appointment_at)


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: DbSession, user: CurrentUser):
    booking = db.scalar(select(Booking).where(Booking.id == booking_id, Booking.user_id == user.id))
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


