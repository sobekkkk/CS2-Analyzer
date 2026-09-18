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
    await route.fulfill({ json: [] });
  });
  await page.route("**/api/v1/matches/match-1/heatmaps/damage", async (route) => {
    await route.fulfill({ json: [] });
  });
  await page.route("**/api/v1/matches/match-1/heatmaps/untraded-deaths", async (route) => {
    await route.fulfill({ json: [] });
  });
  await page.route("**/api/v1/matches/match-1/highlights/opening-kills", async (route) => {
    await route.fulfill({ json: [{ round_number: 0, tick: 80, weapon: "ak47", killer_team: 2, confidence: "direct" }] });
  });
  await page.route("**/api/v1/matches/match-1/heatmaps/five-vs-four", async (route) => {
    await route.fulfill({
      json: [{ cell_x: 1, cell_y: -2, sample_count: 3, round_count: 2, round_numbers: [3, 7] }]
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
  await expect(page.getByRole("heading", { name: "Où vos morts ne sont pas suivies d’un trade" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Vos premiers kills" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Où vous êtes après un avantage 5v4" })).toBeVisible();
  await expect(page.getByLabel(/Cellule 1, -2, 3 positions observées après un 5v4/i)).toBeVisible();
  const openingKill = page.getByRole("button", { name: "Voir la timeline du round 1" });
  await expect(openingKill).toBeVisible();
  await openingKill.click();
  await expect(page.getByRole("button", { name: "Round 1", exact: true })).toHaveClass(/is-selected/);
  await expect(page.getByText("Aucun événement dans ce round.")).toBeVisible();
});
