export type Participant = { id: string; display_name: string };

export type PendingAnalysis = {
  id: string;
  inspection: { participants: Participant[]; source_filename: string; map_name: string };
};

export type MatchOverview = {
  match_id: string;
  map_name: string;
  selected_player: Participant;
  rounds_played: number;
  player_kills: number;
  player_deaths: number;
  damage_received: number;
};

export type TimelineEvent = {
  kind: "damage" | "kill";
  round_number: number;
  tick: number;
  actor_id: string | null;
  actor_name: string | null;
  victim_id: string | null;
  victim_name: string | null;
  weapon: string;
  damage_health: number | null;
};

export type DamageCell = {
  cell_x: number;
  cell_y: number;
  total_damage: number;
  impact_count: number;
  round_count: number;
  round_numbers: number[];
};

export type UntradedDeathCell = {
  cell_x: number;
  cell_y: number;
  occurrence_count: number;
  round_count: number;
  round_numbers: number[];
  death_ticks: number[];
};

export type OpeningKill = {
  round_number: number;
  tick: number;
  weapon: string;
  killer_team: number;
  confidence: "direct";
};

export type FiveVFourCell = {
  cell_x: number;
  cell_y: number;
  sample_count: number;
  round_count: number;
  round_numbers: number[];
};

export type InsightEvidence = {
  round_number: number;
  tick: number;
  kind: "damage" | "kill" | "position_sample";
};

export type Insight = {
  id: string;
  rule_id: "H-01" | "H-02" | "H-03" | "H-04";
  rule_version: string;
  title: string;
  observation: string;
  confidence: "direct" | "inferred";
  occurrence_count: number;
  evidence: InsightEvidence[];
  priority_score: number;
  priority_level: "review" | "context";
  priority_reasons: ("impact" | "repetition" | "direct_evidence" | "inferred_context")[];
  recommendation: string;
};

export class ApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/v1${path}`, init);
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as
      | { detail?: { message?: string } }
      | null;
    throw new ApiError(payload?.detail?.message ?? "L'analyse locale a rencontre une erreur.");
  }
  return response.json() as Promise<T>;
}

export function inspectDemo(file: File): Promise<PendingAnalysis> {
  const body = new FormData();
  body.append("file", file);
  return request<PendingAnalysis>("/demos", { method: "POST", body });
}

export function choosePlayer(analysisId: string, participantId: string): Promise<{ match_id: string }> {
  return request(`/analyses/${analysisId}/player`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ participant_id: participantId })
  });
}

export function getOverview(matchId: string): Promise<MatchOverview> {
  return request(`/matches/${matchId}/overview`);
}

export function getTimeline(matchId: string, roundNumber?: number): Promise<TimelineEvent[]> {
  const suffix = roundNumber === undefined ? "" : `?round_number=${roundNumber}`;
  return request(`/matches/${matchId}/timeline${suffix}`);
}

export function getDamageCells(matchId: string): Promise<DamageCell[]> {
  return request(`/matches/${matchId}/heatmaps/damage`);
}

export function getUntradedDeathCells(matchId: string): Promise<UntradedDeathCell[]> {
  return request(`/matches/${matchId}/heatmaps/untraded-deaths`);
}

export function getOpeningKills(matchId: string): Promise<OpeningKill[]> {
  return request(`/matches/${matchId}/highlights/opening-kills`);
}

export function getFiveVFourCells(matchId: string): Promise<FiveVFourCell[]> {
  return request(`/matches/${matchId}/heatmaps/five-vs-four`);
}

export function getInsights(matchId: string): Promise<Insight[]> {
  return request(`/matches/${matchId}/insights`);
}
