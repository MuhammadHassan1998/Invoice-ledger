from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class InvoiceExport(Base):
    """Tracks every time a PDF is generated for an invoice."""

    __tablename__ = "invoice_exports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    invoice_number: Mapped[str] = mapped_column(String, nullable=False)
    exported_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
