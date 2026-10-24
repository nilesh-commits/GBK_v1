import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "./client";
import { ApiError } from "./types";

afterEach(() => vi.unstubAllGlobals());

describe("api client", () => {
  it("normalizes the backend error shape into ApiError", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response(JSON.stringify({ error: { code: "OUT_OF_SCOPE_DATE", message: "bad date" } }), {
          status: 422,
          headers: { "content-type": "application/json" },
        }),
      ),
    );
    await expect(api.getAccuracy("2026-02-05")).rejects.toMatchObject({
      name: "ApiError",
      code: "OUT_OF_SCOPE_DATE",
      message: "bad date",
    });
  });

  it("raises a NETWORK_ERROR when the backend is unreachable", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new TypeError("failed to fetch");
      }),
    );
    await expect(api.getHealth()).rejects.toBeInstanceOf(ApiError);
    await expect(api.getHealth()).rejects.toHaveProperty("code", "NETWORK_ERROR");
  });

  it("returns parsed JSON on success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response(JSON.stringify({ status: "ok", data_loaded: true, intervals_cached: 42 }), {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      ),
    );
    const health = await api.getHealth();
    expect(health.intervals_cached).toBe(42);
  });
});
