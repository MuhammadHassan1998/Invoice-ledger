import type { InvoiceStatus } from "../types/invoice";

const STATUS_CLASS: Record<InvoiceStatus, string> = {
  paid: "badge badge--paid",
  sent: "badge badge--sent",
  draft: "badge badge--draft",
  overdue: "badge badge--overdue",
  cancelled: "badge badge--cancelled",
};

interface Props {
  status: InvoiceStatus;
}

export function StatusBadge({ status }: Props) {
  return <span className={STATUS_CLASS[status]}>{status}</span>;
}
