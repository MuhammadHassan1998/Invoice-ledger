from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class InvoiceStatus(str, Enum):
    draft = "draft"
    sent = "sent"
    paid = "paid"
    overdue = "overdue"
    cancelled = "cancelled"


class Invoice(BaseModel):
    """A single invoice record that matches the mart_invoices output."""

    # extra="forbid" makes unexpected columns fail fast instead of quietly
    # accepting them.
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    invoice_id: str
    invoice_number: str
    client_name: str
    client_email: EmailStr
    amount: Decimal = Field(decimal_places=2)
    currency: str = Field(max_length=3)
    status: InvoiceStatus
    issued_date: date
    due_date: date
    paid_date: Optional[date] = None
    is_overdue: bool
    days_overdue: int = Field(ge=0)
    collected_amount: Decimal = Field(decimal_places=2)
    description: Optional[str] = None


class InvoiceListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: List[Invoice]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=200)
    total_pages: int = Field(ge=0)


class InvoiceExportRecord(BaseModel):
    """Returned after a PDF is generated; confirms what was exported and when."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    invoice_id: str
    invoice_number: str
    exported_at: datetime
