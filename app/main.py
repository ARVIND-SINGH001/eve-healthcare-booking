from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import auth, bookings, centres, payments
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Alembic is intentionally omitted for this assignment-sized project.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="EVE Healthcare Booking API", lifespan=lifespan)
for router in (auth.router, centres.router, bookings.router, payments.router):
    app.include_router(router)


