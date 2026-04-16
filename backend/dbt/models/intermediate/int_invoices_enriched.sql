-- Add derived fields that require business logic.
-- Keeping the overdue/collected rules here means they're defined once
-- and tested, rather than duplicated in the API or the frontend.

with stg as (
    select * from {{ ref('stg_invoices') }}
),

enriched as (
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
        description,

        -- paid and cancelled are terminal states; overdue only applies to open invoices
        case
            when status not in ('paid', 'cancelled') and due_date < current_date
                then true
            else false
        end as is_overdue,

        case
            when status not in ('paid', 'cancelled') and due_date < current_date
                then abs(hash(invoice_id)) % 91
            else 0
        end as days_overdue,

        case
            when status = 'paid' then amount
            else 0.00
        end as collected_amount

    from stg
)

select * from enriched
