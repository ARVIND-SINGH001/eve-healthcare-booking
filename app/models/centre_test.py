from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CentreTest(Base):
    __tablename__ = "centre_tests"
    __table_args__ = (UniqueConstraint("centre_id", "test_id", name="uq_centre_test"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    centre_id: Mapped[int] = mapped_column(ForeignKey("diagnostic_centres.id", ondelete="CASCADE"), nullable=False, index=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("diagnostic_tests.id", ondelete="CASCADE"), nullable=False, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
