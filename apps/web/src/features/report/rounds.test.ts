import { describe, expect, it } from "vitest";

import { damageTone, displayRound } from "./rounds";

describe("report presentation helpers", () => {
  it("uses player-facing one-based round labels", () => {
    expect(displayRound(0)).toBe("Round 1");
  });

  it("keeps heatmap intensity relative to the current match", () => {
    expect(damageTone(0, 100)).toBe(0);
    expect(damageTone(20, 100)).toBe(1);
    expect(damageTone(50, 100)).toBe(2);
    expect(damageTone(80, 100)).toBe(3);
  });
});
