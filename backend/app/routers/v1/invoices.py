import math
from datetime import datetime
from typing import Optional

import duckdb
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from io import BytesIO
from sqlalchemy.orm import Session

from app.database import get_app_db
from app.db import get_db
from app.models.invoice_export import InvoiceExport
from app.models.user import User
from app.schemas.invoice import Invoice, InvoiceExportRecord, InvoiceListResponse, InvoiceStatus
from app.services.auth import get_current_user
from app.services.pdf import build_invoice_pdf

router = APIRouter(prefix="/invoices", tags=["invoices"])

# dbt writes the mart into a schema named <target>_<schema>, so dev + marts = main_marts
MART_TABLE = "main_marts.mart_invoices"

_COLUMNS = [
    "invoice_id", "invoice_number", "client_name", "client_email",
    "amount", "currency", "status", "issued_date", "due_date", "paid_date",
    "is_overdue", "days_overdue", "collected_amount", "description",
]


def _fetch_one(db: duckdb.DuckDBPyConnection, invoice_id: str) -> Invoice:
    row = db.execute(
        f"SELECT {', '.join(_COLUMNS)} FROM {MART_TABLE} WHERE invoice_id = ?",
        [invoice_id],
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id!r} not found.")
    return Invoice.model_validate(dict(zip(_COLUMNS, row)))


@router.get("", response_model=InvoiceListResponse, summary="List processed invoices")
def list_invoices(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    status: Optional[InvoiceStatus] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: duckdb.DuckDBPyConnection = Depends(get_db),
) -> InvoiceListResponse:
    where_clause = ""
    params: list = []

    if status is not None:
        where_clause = "WHERE status = ?"
        params.append(status.value)

    total: int = db.execute(
        f"SELECT COUNT(*) FROM {MART_TABLE} {where_clause}", params
    ).fetchone()[0]  # type: ignore[index]

    offset = (page - 1) * page_size
    rows = db.execute(
        f"""
        SELECT {', '.join(_COLUMNS)}
        FROM {MART_TABLE}
        {where_clause}
        ORDER BY issued_date DESC
        LIMIT ? OFFSET ?
        """,
        params + [page_size, offset],
    ).fetchall()

    invoices = [Invoice.model_validate(dict(zip(_COLUMNS, row))) for row in rows]

    return InvoiceListResponse(
        data=invoices,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.get("/{invoice_id}/pdf", summary="Download invoice as PDF")
def download_invoice_pdf(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: duckdb.DuckDBPyConnection = Depends(get_db),
    app_db: Session = Depends(get_app_db),
) -> StreamingResponse:
    invoice = _fetch_one(db, invoice_id)

    pdf_bytes = build_invoice_pdf(invoice)

    # Record the export so we have an audit trail
    export = InvoiceExport(
        invoice_id=invoice.invoice_id,
        invoice_number=invoice.invoice_number,
        exported_at=datetime.utcnow(),
    )
    app_db.add(export)
    app_db.commit()

    filename = f"{invoice.invoice_number}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.get("/{invoice_id}/exports", response_model=list[InvoiceExportRecord], summary="PDF export history")
def list_exports(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: duckdb.DuckDBPyConnection = Depends(get_db),
    app_db: Session = Depends(get_app_db),
) -> list[InvoiceExport]:
    # Verify the invoice actually exists before returning export history
    _fetch_one(db, invoice_id)
    return app_db.query(InvoiceExport).filter(InvoiceExport.invoice_id == invoice_id).all()
