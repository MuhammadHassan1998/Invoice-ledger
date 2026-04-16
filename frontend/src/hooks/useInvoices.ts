import { useCallback, useEffect, useReducer } from "react";
import { fetchInvoices } from "../api/invoices";
import type { InvoiceListParams, InvoiceListResponse } from "../types/invoice";

interface State {
  data: InvoiceListResponse | null;
  loading: boolean;
  error: string | null;
}

type Action =
  | { type: "FETCH_START" }
  | { type: "FETCH_SUCCESS"; payload: InvoiceListResponse }
  | { type: "FETCH_ERROR"; payload: string };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "FETCH_START":
      return { ...state, loading: true, error: null };
    case "FETCH_SUCCESS":
      return { data: action.payload, loading: false, error: null };
    case "FETCH_ERROR":
      return { ...state, loading: false, error: action.payload };
  }
}

const initialState: State = { data: null, loading: false, error: null };

export function useInvoices(params: InvoiceListParams = {}, token: string | null) {
  const [state, dispatch] = useReducer(reducer, initialState);

  const load = useCallback(async () => {
    if (!token) return;

    dispatch({ type: "FETCH_START" });
    try {
      const result = await fetchInvoices(params, token);
      dispatch({ type: "FETCH_SUCCESS", payload: result });
    } catch (err) {
      dispatch({
        type: "FETCH_ERROR",
        payload: err instanceof Error ? err.message : "Unknown error",
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.page, params.page_size, params.status, token]);

  useEffect(() => {
    void load();
  }, [load]);

  return { ...state, refetch: load };
}
