import { useEffect, useRef, useState } from "react";
import { ApiError } from "../api/types";

export interface ApiState<T> {
  loading: boolean;
  data: T | null;
  error: ApiError | null;
}

// Fetches data when `deps` change, aborting in-flight requests and discarding
// stale responses (so a slow earlier request can't overwrite a newer one).
export function useApiData<T>(
  fetcher: (signal: AbortSignal) => Promise<T>,
  deps: ReadonlyArray<unknown>,
): ApiState<T> {
  const [state, setState] = useState<ApiState<T>>({ loading: true, data: null, error: null });
  const reqId = useRef(0);

  useEffect(() => {
    const id = ++reqId.current;
    const controller = new AbortController();
    setState((s) => ({ ...s, loading: true, error: null }));

    fetcher(controller.signal)
      .then((data) => {
        if (id === reqId.current) setState({ loading: false, data, error: null });
      })
      .catch((err) => {
        if (controller.signal.aborted || id !== reqId.current) return;
        const apiErr =
          err instanceof ApiError ? err : new ApiError("UNKNOWN", err?.message ?? "Unexpected error");
        setState({ loading: false, data: null, error: apiErr });
      });

    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return state;
}
