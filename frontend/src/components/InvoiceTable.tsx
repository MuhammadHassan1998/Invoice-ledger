import type { Invoice } from "../types/invoice";
import { downloadInvoicePdf } from "../api/invoices";
import { StatusBadge } from "./StatusBadge";

interface Props {
  invoices: Invoice[];
  token: string;
}

function formatCurrency(amount: string, currency: string): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
  }).format(Number(amount));
}

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function DownloadButton({ invoiceId, token }: { invoiceId: string; token: string }) {
  async function handleClick() {
    await downloadInvoicePdf(invoiceId, token);
  }

  return (
    <button className="pdf-btn" onClick={handleClick} title="View invoice PDF">
      View
    </button>
  );
}

export function InvoiceTable({ invoices, token }: Props) {
  if (invoices.length === 0) {
    return <p className="empty-state">No invoices found.</p>;
  }

  return (
    <div className="table-wrapper">
      <table className="invoice-table">
        <thead>
          <tr>
            <th>Invoice #</th>
            <th>Client</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Issued</th>
            <th>Due</th>
            <th>Paid</th>
            <th>Days Overdue</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {invoices.map((inv) => (
            <tr key={inv.invoice_id} className={inv.is_overdue ? "row--overdue" : ""}>
              <td className="mono">{inv.invoice_number}</td>
              <td>
                <div className="client-name">{inv.client_name}</div>
                <div className="client-email">{inv.client_email}</div>
              </td>
              <td className="mono amount">{formatCurrency(inv.amount, inv.currency)}</td>
              <td>
                <StatusBadge status={inv.status} />
              </td>
              <td>{formatDate(inv.issued_date)}</td>
              <td>{formatDate(inv.due_date)}</td>
              <td>{formatDate(inv.paid_date)}</td>
              <td className={inv.days_overdue > 0 ? "overdue-days" : ""}>
                {inv.days_overdue > 0 ? `${inv.days_overdue}d` : "—"}
              </td>
              <td>
                <DownloadButton invoiceId={inv.invoice_id} token={token} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
