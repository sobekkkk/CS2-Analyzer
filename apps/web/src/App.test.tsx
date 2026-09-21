import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
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

  it("opens source evidence on demand without reserving report space", async () => {
    const response = (payload: object) => Promise.resolve(new Response(JSON.stringify(payload)));
    vi.stubGlobal("fetch", vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/demos")) return response({ id: "pending-1", inspection: { source_filename: "mirage.dem", map_name: "de_mirage", participants: [{ id: "target", display_name: "Sobek" }] } });
      if (url.endsWith("/analyses/pending-1/player")) return response({ match_id: "match-1" });
      if (url.endsWith("/overview")) return response({ match_id: "match-1", map_name: "de_mirage", selected_player: { id: "target", display_name: "Sobek" }, rounds_played: 13, player_kills: 17, player_deaths: 12, damage_received: 921 });
      if (url.endsWith("/heatmaps/damage")) return response([{ cell_x: 2, cell_y: -3, total_damage: 180, impact_count: 3, round_count: 1, round_numbers: [1] }]);
      if (url.endsWith("/heatmaps/untraded-deaths")) return response([{ cell_x: 1, cell_y: -2, occurrence_count: 2, round_count: 2, round_numbers: [3, 7], death_ticks: [1200, 2400] }]);
      if (url.endsWith("/highlights/opening-kills")) return response([{ round_number: 0, tick: 80, weapon: "ak47" }]);
      if (url.endsWith("/heatmaps/five-vs-four")) return response([{ cell_x: 1, cell_y: -2, sample_count: 3, round_count: 2, round_numbers: [3, 7] }]);
      if (url.endsWith("/insights")) return response([
        { id: "H-01:1:-2", rule_id: "H-01", rule_version: "0.1", title: "Morts sans trade observées", observation: "2 morts non suivies d’un trade dans cette zone de grille.", confidence: "inferred", occurrence_count: 2, evidence: [{ round_number: 3, tick: 1200, kind: "kill" }], priority_score: 80, priority_level: "review", priority_reasons: ["impact", "repetition", "inferred_context"], recommendation: "Ouvrez le round source pour vérifier la séquence avant d’en tirer une conclusion." },
        { id: "H-04:2:-3", rule_id: "H-04", rule_version: "0.1", title: "HP perdus dans cette zone", observation: "180 HP reçus sur 3 impacts dans cette zone de grille.", confidence: "direct", occurrence_count: 3, evidence: [{ round_number: 1, tick: 240, kind: "damage" }], priority_score: 73, priority_level: "review", priority_reasons: ["impact", "repetition", "direct_evidence"], recommendation: "Relisez le round source avant d’en déduire une habitude de positionnement." },
        { id: "H-03:1:-2", rule_id: "H-03", rule_version: "0.1", title: "Position après un avantage 5v4", observation: "3 positions relevées dans cette zone après un avantage 5v4.", confidence: "inferred", occurrence_count: 3, evidence: [{ round_number: 3, tick: 1200, kind: "position_sample" }], priority_score: 39, priority_level: "context", priority_reasons: ["repetition", "inferred_context"], recommendation: "Comparez ce placement à la suite du round source." }
      ]);
      if (url.includes("/timeline?round_number=0")) return response([{ kind: "kill", round_number: 0, tick: 90, actor_id: "target", actor_name: "Sobek", victim_id: "enemy", victim_name: "Enemy", weapon: "ak47" }]);
      if (url.includes("/timeline?round_number=1")) return response([{ kind: "damage", round_number: 1, tick: 240, actor_id: "enemy", actor_name: "Enemy", victim_id: "target", victim_name: "Sobek", weapon: "m4a1", damage_health: 32 }]);
      if (url.includes("/timeline?round_number=3")) return response([{ kind: "kill", round_number: 3, tick: 1200, actor_id: "enemy", actor_name: "Enemy", victim_id: "target", victim_name: "Sobek", weapon: "m4a1" }]);
      if (url.endsWith("/timeline")) return response([{ kind: "kill", round_number: 0, tick: 90, actor_id: "target", actor_name: "Sobek", victim_id: "enemy", victim_name: "Enemy", weapon: "ak47" }]);
      throw new Error(`Unhandled request: ${url}`);
    }));

    render(<App />);
    fireEvent.change(screen.getByLabelText("Importer une démo CS2"), {
      target: { files: [new File(["demo"], "mirage.dem", { type: "application/octet-stream" })] }
    });
    fireEvent.click(await screen.findByRole("button", { name: "Sobek" }));

    expect(await screen.findByRole("heading", { name: "Où vos morts ne sont pas suivies d’un trade" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Priorités à examiner" })).toBeVisible();
    expect(screen.getByText(/Signal à vérifier · contexte inféré/)).toBeVisible();
    expect(screen.getByText(/classement est fondé sur l’impact/i)).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: /ouvrir la preuve : morts sans trade observées/i }));
    expect(await screen.findByRole("dialog", { name: "Preuve du round 4" })).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: "Fermer la preuve" }));
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
    expect(screen.getByRole("button", { name: "Voir la preuve du round 2" })).toBeVisible();
    expect(screen.getByLabelText(/Cellule 1, -2, 2 morts sans trade observées/i)).toBeVisible();
    expect(screen.getByRole("button", { name: "Voir la preuve du round 4" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Vos premiers kills" })).toBeVisible();
    expect(screen.getByRole("button", { name: "Voir la timeline du round 1" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Où vous êtes après un avantage 5v4" })).toBeVisible();
    expect(screen.getByRole("button", { name: /Voir la preuve du round 4 : cellule 1, -2, 3 positions observées après un 5v4/i })).toBeVisible();
    expect(screen.getByLabelText("Carte de grille monde : positions après un avantage 5v4")).toBeVisible();
    const fiveVFourPanel = screen.getByRole("heading", { name: "Où vous êtes après un avantage 5v4" }).closest("section");
    expect(fiveVFourPanel).not.toBeNull();
    expect(within(fiveVFourPanel!).getByRole("button", { name: /Voir la preuve du round 4/i })).toBeVisible();
    expect(screen.queryByRole("heading", { name: "Timeline" })).not.toBeInTheDocument();
    expect(screen.queryByText("Sélectionnez un round pour lire les événements sources.")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Voir la timeline du round 1" }));

    expect(await screen.findByRole("dialog", { name: "Preuve du round 1" })).toBeVisible();
    expect(await screen.findByLabelText("Événements du round")).toBeVisible();
    expect(screen.getByText("Vous")).toBeVisible();
    expect(screen.getByText("Enemy")).toBeVisible();

    fireEvent.click(screen.getByRole("button", { name: "Fermer la preuve" }));
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());

    fireEvent.click(screen.getByRole("button", { name: "Voir la preuve du round 4" }));

    expect(await screen.findByRole("dialog", { name: "Preuve du round 4" })).toBeVisible();
    await waitFor(() => {
      expect(screen.getByLabelText("Événements du round")).toHaveTextContent("Enemy élimine Vous");
    });

    fireEvent.click(screen.getByRole("button", { name: "Fermer la preuve" }));
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());

    fireEvent.click(screen.getByRole("button", { name: "Voir la preuve du round 2" }));

    expect(await screen.findByRole("dialog", { name: "Preuve du round 2" })).toBeVisible();
    await waitFor(() => {
      expect(screen.getByLabelText("Événements du round")).toHaveTextContent("Enemy inflige des dégâts à Vous · 32 HP");
    });

    fireEvent.click(screen.getByRole("button", { name: "Fermer la preuve" }));
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());

    fireEvent.click(within(fiveVFourPanel!).getByRole("button", { name: /Voir la preuve du round 4/i }));
    expect(await screen.findByRole("dialog", { name: "Preuve du round 4" })).toBeVisible();
  });
});
