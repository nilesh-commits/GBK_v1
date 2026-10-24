import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiError } from "../api/types";
import { StateBoundary } from "./StateBoundary";

describe("StateBoundary", () => {
  it("shows a loading state", () => {
    render(
      <StateBoundary loading error={null}>
        child
      </StateBoundary>,
    );
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("shows the error message and code", () => {
    render(
      <StateBoundary loading={false} error={new ApiError("OUT_OF_SCOPE_DATE", "bad date")}>
        child
      </StateBoundary>,
    );
    const alert = screen.getByRole("alert");
    expect(alert).toHaveTextContent("bad date");
    expect(alert).toHaveTextContent("OUT_OF_SCOPE_DATE");
  });

  it("renders children when healthy", () => {
    render(
      <StateBoundary loading={false} error={null}>
        <div>content</div>
      </StateBoundary>,
    );
    expect(screen.getByText("content")).toBeInTheDocument();
  });

  it("shows the empty message", () => {
    render(
      <StateBoundary loading={false} error={null} empty emptyMessage="nothing here">
        <div>content</div>
      </StateBoundary>,
    );
    expect(screen.getByText("nothing here")).toBeInTheDocument();
  });
});
