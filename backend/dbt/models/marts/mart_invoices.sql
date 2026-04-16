-- Stable table the API queries directly. Columns are an explicit allowlist:
-- adding something to intermediate doesn't automatically expose it here.
-- Materialised as a table so reads are fast without re-running the chain.

{{
    config(
        materialized='table',
        unique_key='invoice_id'
    )
}}

with int_invoices as (
    select * from {{ ref('int_invoices_enriched') }}
)

select
    invoice_id,
    invoice_number,
    client_name,
    client_email,
    amount,
    currency,
    status,
    issued_date,
    due_date,
    paid_date,
    is_overdue,
    days_overdue,
    collected_amount,
    description
from int_invoices
order by issued_date desc
