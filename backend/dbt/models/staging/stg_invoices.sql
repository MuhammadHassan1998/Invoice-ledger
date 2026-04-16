-- Rename and cast raw columns. No logic here; just making the source
-- usable for downstream models. If the CSV schema changes, this is the
-- only file that needs to know about it.

with source as (
    select * from {{ ref('raw_invoices') }}
),

renamed as (
    select
        cast(id             as varchar)        as invoice_id,
        cast(invoice_number as varchar)        as invoice_number,
        cast(client_name    as varchar)        as client_name,
        cast(client_email   as varchar)        as client_email,
        cast(amount         as decimal(18,2))  as amount,
        cast(currency       as varchar)        as currency,
        cast(status         as varchar)        as status,
        cast(issued_at      as date)           as issued_date,
        cast(due_at         as date)           as due_date,
        nullif(cast(paid_at as varchar), '')::date as paid_date,
        cast(description    as varchar)        as description
    from source
)

select * from renamed
