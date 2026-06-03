import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "./App";

describe("App", () => {
  it("renders the Phase 2 shell", () => {
    render(<App />);

    expect(screen.getByText("ApplyWise AI")).toBeInTheDocument();
    expect(screen.getByText("No auto-submit workflows")).toBeInTheDocument();
  });
});

