export function displayRound(roundNumber: number): string {
  return `Round ${roundNumber + 1}`;
}

export function damageTone(totalDamage: number, maximumDamage: number): 0 | 1 | 2 | 3 {
  if (maximumDamage <= 0 || totalDamage <= 0) return 0;
  const ratio = totalDamage / maximumDamage;
  if (ratio >= 0.75) return 3;
  if (ratio >= 0.4) return 2;
  return 1;
}
