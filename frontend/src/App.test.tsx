import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        status: 401,
        ok: false
      })
    );
  });

  it("renders the Phase 4 shell", () => {
    render(<App />);

    expect(screen.getByText("ApplyWise AI")).toBeInTheDocument();
    expect(screen.getByText("No auto-submit workflows")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Sign in with Google" })).toBeInTheDocument();
  });
});
