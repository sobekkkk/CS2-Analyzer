import { expect, test } from "@playwright/test";

test("a local import reaches the player report without a real demo upload", async ({ page }) => {
  await page.route("**/api/v1/demos", async (route) => {
    await route.fulfill({
      json: {
        id: "pending-1",
        inspection: {
          source_filename: "mirage.dem",
          map_name: "de_mirage",
          participants: [{ id: "target", display_name: "Sobek" }]
        }
      }
    });
  });
  await page.route("**/api/v1/analyses/pending-1/player", async (route) => {
    await route.fulfill({ json: { match_id: "match-1" } });
  });
  await page.route("**/api/v1/matches/match-1/overview", async (route) => {
    await route.fulfill({
      json: {
        match_id: "match-1",
        map_name: "de_mirage",
        selected_player: { id: "target", display_name: "Sobek" },
        rounds_played: 13,
        player_kills: 17,
        player_deaths: 12,
        damage_received: 921
      }
    });
  });
  await page.route("**/api/v1/matches/match-1/timeline**", async (route) => {
    await route.fulfill({
      json: [
        {
          kind: "damage",
          round_number: 0,
          tick: 90,
          actor_id: "opponent",
          actor_name: "Opponent",
          victim_id: "target",
          victim_name: "Sobek",
          weapon: "ak47",
          damage_health: 16
        }
      ]
    });
  });
  await page.route("**/api/v1/matches/match-1/heatmaps/damage", async (route) => {
    await route.fulfill({
      json: [{ cell_x: 2, cell_y: -3, total_damage: 180, impact_count: 3, round_count: 1, round_numbers: [0] }]
    });
  });
  await page.route("**/api/v1/matches/match-1/heatmaps/untraded-deaths", async (route) => {
    await route.fulfill({
      json: [{ cell_x: 1, cell_y: -2, occurrence_count: 2, round_count: 2, round_numbers: [3, 7], death_ticks: [1200, 2400] }]
    });
  });
  await page.route("**/api/v1/matches/match-1/highlights/opening-kills", async (route) => {
    await route.fulfill({ json: [{ round_number: 0, tick: 80, weapon: "ak47", killer_team: 2, confidence: "direct" }] });
  });
  await page.route("**/api/v1/matches/match-1/heatmaps/five-vs-four", async (route) => {
    await route.fulfill({
      json: [{ cell_x: 1, cell_y: -2, sample_count: 3, round_count: 2, round_numbers: [3, 7] }]
    });
  });
  await page.route("**/api/v1/matches/match-1/insights", async (route) => {
    await route.fulfill({
      json: [
        {
          id: "H-01:1:-2",
          rule_id: "H-01",
          rule_version: "0.1",
          title: "Morts sans trade observées",
          observation: "2 morts non suivies d’un trade dans cette zone de grille.",
          confidence: "inferred",
          occurrence_count: 2,
          evidence: [{ round_number: 3, tick: 1200, kind: "kill" }],
          priority_score: 80,
          priority_level: "review",
          priority_reasons: ["impact", "repetition", "inferred_context"],
          recommendation: "Ouvrez le round source pour vérifier la séquence avant d’en tirer une conclusion."
        }
      ]
    });
  });

  await page.goto("/");
  await page.getByLabel("Importer une démo CS2").setInputFiles({
    name: "mirage.dem",
    mimeType: "application/octet-stream",
    buffer: Buffer.from("test demo")
  });
  await page.getByRole("button", { name: "Sobek" }).click();

  await expect(page.getByRole("heading", { name: "Sobek" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Priorités à examiner" })).toBeVisible();
  await expect(page.getByText(/Signal à vérifier · contexte inféré/)).toBeVisible();
  await page.getByRole("button", { name: /Ouvrir la preuve : Morts sans trade observées/i }).click();
  await expect(page.getByRole("dialog", { name: "Preuve du round 4" })).toBeVisible();
  await page.getByRole("button", { name: "Fermer la preuve" }).click();
  await expect(page.getByRole("heading", { name: "Où vos morts ne sont pas suivies d’un trade" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Vos premiers kills" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Où vous êtes après un avantage 5v4" })).toBeVisible();
  await expect(page.getByRole("button", { name: /Voir la preuve du round 4 : cellule 1, -2, 3 positions observées après un 5v4/i })).toBeVisible();
  await expect(page.getByLabel("Carte de grille monde : positions après un avantage 5v4")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Timeline" })).toHaveCount(0);
  const openingKill = page.getByRole("button", { name: "Voir la timeline du round 1" });
  await expect(openingKill).toBeVisible();
  await openingKill.click();
  await expect(page.getByRole("dialog", { name: "Preuve du round 1" })).toBeVisible();
  await expect(page.getByText("Opponent inflige des dégâts à Vous · 16 HP")).toBeVisible();
  await page.getByRole("button", { name: "Fermer la preuve" }).click();
  await expect(page.getByRole("dialog", { name: "Preuve du round 1" })).toHaveCount(0);

  const untradedDeathProof = page.locator("section.panel--untraded").getByRole("button", { name: "Voir la preuve du round 4" });
  await expect(untradedDeathProof).toBeVisible();
  await untradedDeathProof.click();
  await expect(page.getByRole("dialog", { name: "Preuve du round 4" })).toBeVisible();
  await page.getByRole("button", { name: "Fermer la preuve" }).click();

  const damageProof = page.getByRole("button", { name: "Voir la preuve du round 1" });
  await expect(damageProof).toBeVisible();
  await damageProof.click();
  await expect(page.getByRole("dialog", { name: "Preuve du round 1" })).toBeVisible();
  await page.getByRole("button", { name: "Fermer la preuve" }).click();

  const fiveVFourProof = page.locator("section.panel--five-v-four").getByRole("button", { name: /Voir la preuve du round 4/i });
  await fiveVFourProof.click();
  await expect(page.getByRole("dialog", { name: "Preuve du round 4" })).toBeVisible();
});
