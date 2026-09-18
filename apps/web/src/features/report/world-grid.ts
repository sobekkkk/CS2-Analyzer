export type WorldGridCell = { cell_x: number; cell_y: number };

export type WorldViewport = {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
};

export type WorldGridPoint = { left: number; top: number };

/**
 * Construit un repere explicite de cellules monde, sans pretendre dessiner
 * le radar ni les callouts de Mirage. Une marge d'une cellule evite de coller
 * les observations aux bords du panneau.
 */
export function createWorldViewport(cells: WorldGridCell[]): WorldViewport | null {
  const validCells = cells.filter((cell) => Number.isFinite(cell.cell_x) && Number.isFinite(cell.cell_y));
  if (validCells.length === 0) return null;
  return {
    minX: Math.min(...validCells.map((cell) => cell.cell_x)) - 1,
    maxX: Math.max(...validCells.map((cell) => cell.cell_x)) + 1,
    minY: Math.min(...validCells.map((cell) => cell.cell_y)) - 1,
    maxY: Math.max(...validCells.map((cell) => cell.cell_y)) + 1
  };
}

export function worldGridPoint(cell: WorldGridCell, viewport: WorldViewport): WorldGridPoint {
  const width = viewport.maxX - viewport.minX;
  const height = viewport.maxY - viewport.minY;
  return {
    left: Number((((cell.cell_x - viewport.minX) / width) * 100).toFixed(3)),
    top: Number((((viewport.maxY - cell.cell_y) / height) * 100).toFixed(3))
  };
}
