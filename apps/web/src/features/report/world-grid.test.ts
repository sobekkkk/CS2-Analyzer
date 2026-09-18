import { describe, expect, it } from "vitest";

import { createWorldViewport, worldGridPoint } from "./world-grid";

describe("world grid projection", () => {
  it("keeps distant cells spatially separated while inverting the world Y axis", () => {
    const viewport = createWorldViewport([
      { cell_x: -2, cell_y: 1 },
      { cell_x: 2, cell_y: -3 }
    ]);

    expect(viewport).toEqual({ minX: -3, maxX: 3, minY: -4, maxY: 2 });
    if (!viewport) throw new Error("Expected a viewport for non-empty cells");
    expect(worldGridPoint({ cell_x: -2, cell_y: 1 }, viewport)).toEqual({ left: 16.667, top: 16.667 });
    expect(worldGridPoint({ cell_x: 2, cell_y: -3 }, viewport)).toEqual({ left: 83.333, top: 83.333 });
  });

  it("returns no viewport for an empty heatmap", () => {
    expect(createWorldViewport([])).toBeNull();
  });
});
