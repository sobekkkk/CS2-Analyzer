import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "./App";

describe("App", () => {
  it("presents a local-first import entry point before a demo is selected", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Comprendre une partie, pas distribuer des notes." })).toBeVisible();
    expect(screen.getByLabelText("Importer une démo CS2")).toHaveAttribute("accept", ".dem");
    expect(screen.getByRole("heading", { name: "Commencez par une démo terminée" })).toBeVisible();
    expect(screen.getByText(/seule une table dérivée pseudonymisée est conservée/i)).toBeVisible();
  });
});
