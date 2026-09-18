import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";

describe("App", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("presents a local-first import entry point before a demo is selected", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Comprendre une partie, pas distribuer des notes." })).toBeVisible();
    expect(screen.getByLabelText("Importer une démo CS2")).toHaveAttribute("accept", ".dem");
    expect(screen.getByRole("heading", { name: "Commencez par une démo terminée" })).toBeVisible();
    expect(screen.getByText(/seule une table dérivée pseudonymisée est conservée/i)).toBeVisible();
  });

  it("renders the H-01 grid after a local player selection", async () => {
    const response = (payload: object) => Promise.resolve(new Response(JSON.stringify(payload)));
    vi.stubGlobal(
      "fetch",
      vi.fn()
        .mockImplementationOnce(() => response({
          id: "pending-1",
          inspection: {
            source_filename: "mirage.dem",
            map_name: "de_mirage",
            participants: [{ id: "target", display_name: "Sobek" }]
          }
        }))
        .mockImplementationOnce(() => response({ match_id: "match-1" }))
        .mockImplementationOnce(() => response({
          match_id: "match-1",
          map_name: "de_mirage",
          selected_player: { id: "target", display_name: "Sobek" },
          rounds_played: 13,
          player_kills: 17,
          player_deaths: 12,
          damage_received: 921
        }))
        .mockImplementationOnce(() => response([]))
        .mockImplementationOnce(() => response([]))
        .mockImplementationOnce(() => response([
          {
            cell_x: 1,
            cell_y: -2,
            occurrence_count: 2,
            round_count: 2,
            round_numbers: [3, 7],
            death_ticks: [1200, 2400]
          }
        ]))
        .mockImplementationOnce(() => response([
          {
            round_number: 0,
            tick: 80,
            weapon: "ak47"
          }
        ]))
    );

    render(<App />);
    fireEvent.change(screen.getByLabelText("Importer une démo CS2"), {
      target: { files: [new File(["demo"], "mirage.dem", { type: "application/octet-stream" })] }
    });
    fireEvent.click(await screen.findByRole("button", { name: "Sobek" }));

    expect(await screen.findByRole("heading", { name: "Où vos morts ne sont pas suivies d’un trade" })).toBeVisible();
    expect(screen.getByLabelText(/Cellule 1, -2, 2 morts sans trade observées/i)).toBeVisible();
    expect(screen.getByRole("heading", { name: "Vos premiers kills" })).toBeVisible();
    expect(screen.getByRole("button", { name: "Voir la timeline du round 1" })).toBeVisible();
  });
});
