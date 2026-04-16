// These types are kept in sync with the backend schema by hand.
// If the backend contract changes, update this file too.

export type InvoiceStatus = "draft" | "sent" | "paid" | "overdue" | "cancelled";

export interface Invoice {
  invoice_id: string;
  invoice_number: string;
  client_name: string;
  client_email: string;
  amount: string; // Decimal serialised as string to preserve precision
  currency: string;
  status: InvoiceStatus;
  issued_date: string;
  due_date: string;
  paid_date: string | null;
  is_overdue: boolean;
  days_overdue: number;
  collected_amount: string;
  description: string | null;
}

export interface InvoiceListResponse {
  data: Invoice[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface InvoiceListParams {
  page?: number;
  page_size?: number;
  status?: InvoiceStatus | "";
}
