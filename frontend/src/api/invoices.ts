import type { InvoiceListParams, InvoiceListResponse } from "../types/invoice";

const BASE_URL = "/api/v1";

export async function fetchInvoices(
  params: InvoiceListParams = {},
  token: string
): Promise<InvoiceListResponse> {
  const query = new URLSearchParams();

  if (params.page) query.set("page", String(params.page));
  if (params.page_size) query.set("page_size", String(params.page_size));
  if (params.status) query.set("status", params.status);

  const url = `${BASE_URL}/invoices${query.size > 0 ? `?${query}` : ""}`;
  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`API error ${response.status}: ${detail}`);
  }

  return response.json() as Promise<InvoiceListResponse>;
}

export async function downloadInvoicePdf(invoiceId: string, token: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/invoices/${invoiceId}/pdf`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`API error ${response.status}: ${detail}`);
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.target = "_blank";
  link.rel = "noreferrer";
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
