import { useState } from "react";
import { AuthPanel } from "./components/AuthPanel";
import { InvoiceTable } from "./components/InvoiceTable";
import { useAuth } from "./hooks/useAuth";
import { useInvoices } from "./hooks/useInvoices";
import type { InvoiceListParams, InvoiceStatus } from "./types/invoice";

const PAGE_SIZE = 10;
const STATUS_OPTIONS: Array<{ label: string; value: InvoiceStatus | "" }> = [
  { label: "All", value: "" },
  { label: "Draft", value: "draft" },
  { label: "Sent", value: "sent" },
  { label: "Paid", value: "paid" },
  { label: "Overdue", value: "overdue" },
  { label: "Cancelled", value: "cancelled" },
];

export default function App() {
  const { session, token, user, setSession, logout } = useAuth();
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState<InvoiceStatus | "">("");

  const params: InvoiceListParams = { page, page_size: PAGE_SIZE, status };
  const { data, loading, error } = useInvoices(params, token);

  function handleStatusChange(next: InvoiceStatus | "") {
    setStatus(next);
    setPage(1);
  }

  if (!session || !token) {
    return <AuthPanel onAuthenticated={setSession} />;
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <p className="eyebrow">Invoice Ledger</p>
          <h1>Processed invoices</h1>
          <p className="page-description">
            A clean list of invoices generated from the dbt mart, with status
            filtering and quick PDF access.
          </p>
        </div>
        <div className="header-actions">
          {data && (
            <div className="header-chip">
              <span>{data.total}</span> records
            </div>
          )}
          <div className="user-menu">
            <span>{user?.username}</span>
            <button type="button" onClick={logout}>
              Log out
            </button>
          </div>
        </div>
      </header>

      <div className="toolbar">
        <div className="filter-group">
          <label htmlFor="status-filter">Status</label>
          <select
            id="status-filter"
            value={status}
            onChange={(e) => handleStatusChange(e.target.value as InvoiceStatus | "")}
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading && <div className="state-overlay">Loading…</div>}
      {error && <div className="state-overlay error">Error: {error}</div>}
      {data && !loading && <InvoiceTable invoices={data.data} token={token} />}

      {data && data.total_pages > 1 && (
        <div className="pagination">
          <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
            Previous
          </button>
          <span>
            Page {data.page} of {data.total_pages}
          </span>
          <button
            disabled={page >= data.total_pages}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
