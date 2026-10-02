from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DiagnosticCentre(Base):
    __tablename__ = "diagnostic_centres"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
