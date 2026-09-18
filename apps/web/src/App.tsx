import { useMemo, useState } from "react";
import { Button } from "react-aria-components";

import {
  choosePlayer,
  getDamageCells,
  getOverview,
  getTimeline,
  inspectDemo,
  type DamageCell,
  type MatchOverview,
  type Participant,
  type TimelineEvent
} from "./api/client";
import { damageTone, displayRound } from "./features/report/rounds";

type ViewState =
  | { kind: "empty" }
  | { kind: "inspecting"; filename: string }
  | { kind: "choosing-player"; analysisId: string; filename: string; participants: Participant[] }
  | { kind: "loading-report"; filename: string }
  | {
      kind: "ready";
      filename: string;
      overview: MatchOverview;
      timeline: TimelineEvent[];
      damageCells: DamageCell[];
      selectedRound: number | undefined;
    }
  | { kind: "error"; message: string };

function friendlyEventActor(event: TimelineEvent, playerId: string): string {
  return event.actor_id === playerId ? "Vous" : "Un autre joueur";
}

function Timeline({ events, playerId }: { events: TimelineEvent[]; playerId: string }) {
  if (events.length === 0) {
    return <p className="empty-copy">Aucun événement dans ce round.</p>;
  }
  return (
    <ol className="timeline-list" aria-label="Événements du round">
      {events.map((event) => (
        <li className="timeline-event" key={`${event.kind}-${event.tick}-${event.victim_id}`}>
          <span className={`event-mark event-mark--${event.kind}`} aria-hidden="true" />
          <div>
            <p>
              <strong>{friendlyEventActor(event, playerId)}</strong>{" "}
              {event.kind === "kill" ? "élimine" : "inflige des dégâts à"} un autre joueur
              {event.damage_health ? ` · ${event.damage_health} HP` : ""}
            </p>
            <span>Tick {event.tick.toLocaleString("fr-FR")} · {event.weapon}</span>
          </div>
        </li>
      ))}
    </ol>
  );
}

function DamageGrid({ cells }: { cells: DamageCell[] }) {
  const maximumDamage = Math.max(0, ...cells.map((cell) => cell.total_damage));
  if (cells.length === 0) {
    return <p className="empty-copy">Pas assez de données fiables pour afficher les zones de dégâts.</p>;
  }
  return (
    <div className="zone-grid" aria-label="Grille des dégâts subis">
      {cells.map((cell) => {
        const tone = damageTone(cell.total_damage, maximumDamage);
        return (
          <article
            className={`zone-cell zone-cell--tone-${tone}`}
            key={`${cell.cell_x}-${cell.cell_y}`}
            aria-label={`Cellule ${cell.cell_x}, ${cell.cell_y}, ${cell.total_damage} HP subis sur ${cell.impact_count} impacts`}
          >
            <span className="zone-coordinates">{cell.cell_x} / {cell.cell_y}</span>
            <strong>{cell.total_damage} <small>HP</small></strong>
            <span>{cell.impact_count} impact{cell.impact_count > 1 ? "s" : ""} · {cell.round_count} round{cell.round_count > 1 ? "s" : ""}</span>
          </article>
        );
      })}
    </div>
  );
}

export function App() {
  const [view, setView] = useState<ViewState>({ kind: "empty" });
  const [isRoundLoading, setIsRoundLoading] = useState(false);

  const activeReport = view.kind === "ready" ? view : null;
  const roundNumbers = useMemo(
    () => activeReport ? Array.from({ length: activeReport.overview.rounds_played }, (_, index) => index) : [],
    [activeReport]
  );

  async function loadReport(matchId: string, filename: string) {
    const [overview, timeline, damageCells] = await Promise.all([
      getOverview(matchId),
      getTimeline(matchId),
      getDamageCells(matchId)
    ]);
    setView({ kind: "ready", filename, overview, timeline, damageCells, selectedRound: undefined });
  }

  async function handleDemoSelection(file: File | undefined) {
    if (!file) return;
    setView({ kind: "inspecting", filename: file.name });
    try {
      const pending = await inspectDemo(file);
      setView({
        kind: "choosing-player",
        analysisId: pending.id,
        filename: pending.inspection.source_filename,
        participants: pending.inspection.participants
      });
    } catch (error) {
      setView({ kind: "error", message: error instanceof Error ? error.message : "Import impossible." });
    }
  }

  async function handlePlayerSelection(participant: Participant) {
    if (view.kind !== "choosing-player") return;
    const { analysisId, filename } = view;
    setView({ kind: "loading-report", filename });
    try {
      const result = await choosePlayer(analysisId, participant.id);
      await loadReport(result.match_id, filename);
    } catch (error) {
      setView({ kind: "error", message: error instanceof Error ? error.message : "Analyse impossible." });
    }
  }

  async function selectRound(roundNumber: number | undefined) {
    if (!activeReport) return;
    setIsRoundLoading(true);
    try {
      const timeline = await getTimeline(activeReport.overview.match_id, roundNumber);
      setView({ ...activeReport, timeline, selectedRound: roundNumber });
    } catch (error) {
      setView({ kind: "error", message: error instanceof Error ? error.message : "Timeline indisponible." });
    } finally {
      setIsRoundLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="CS2 Round Analyzer, accueil">
          <span className="brand-mark" aria-hidden="true">CS</span>
          <span>Round Analyzer</span>
        </a>
        <span className="environment-label">Local · Mirage alpha</span>
      </header>

      <main className="content">
        <section className="page-heading">
          <div>
            <p className="eyebrow">Débrief post-match</p>
            <h1>Comprendre une partie, pas distribuer des notes.</h1>
            <p>Les observations restent liées aux rounds et aux événements sources de votre démo.</p>
          </div>
          <label className="upload-button">
            <input
              accept=".dem"
              aria-label="Importer une démo CS2"
              onChange={(event) => void handleDemoSelection(event.currentTarget.files?.[0])}
              type="file"
            />
            Importer une démo
          </label>
        </section>

        {view.kind === "empty" && (
          <section className="empty-state" aria-live="polite">
            <span className="empty-state__index">01</span>
            <div>
              <h2>Commencez par une démo terminée</h2>
              <p>Le fichier est traité localement. Après le choix du joueur, seule une table dérivée pseudonymisée est conservée.</p>
            </div>
          </section>
        )}

        {view.kind === "inspecting" && <section className="notice">Lecture de <strong>{view.filename}</strong>…</section>}

        {view.kind === "choosing-player" && (
          <section className="player-picker" aria-live="polite">
            <p className="eyebrow">Étape 2 · Joueur analysé</p>
            <h2>Quel pseudo souhaitez-vous analyser ?</h2>
            <p className="panel-description">Ce choix est enregistré localement pour proposer le même profil lors du prochain import.</p>
            <div className="player-grid">
              {view.participants.map((participant) => (
                <Button className="player-choice" key={participant.id} onPress={() => void handlePlayerSelection(participant)}>
                  {participant.display_name}
                </Button>
              ))}
            </div>
          </section>
        )}

        {view.kind === "loading-report" && <section className="notice">Construction du rapport pour <strong>{view.filename}</strong>…</section>}

        {view.kind === "error" && (
          <section className="error-notice" role="alert">
            <h2>Analyse non disponible</h2>
            <p>{view.message}</p>
            <Button className="text-button" onPress={() => setView({ kind: "empty" })}>Revenir à l’import</Button>
          </section>
        )}

        {activeReport && (
          <>
            <section className="report-heading" aria-live="polite">
              <div>
                <p className="eyebrow">Rapport · {activeReport.overview.map_name}</p>
                <h2>{activeReport.overview.selected_player.display_name}</h2>
                <p>{activeReport.filename}</p>
              </div>
              <Button className="text-button" onPress={() => setView({ kind: "empty" })}>Analyser une autre démo</Button>
            </section>

            <section className="metric-strip" aria-label="Récapitulatif du match">
              <article><span>Rounds</span><strong>{activeReport.overview.rounds_played}</strong></article>
              <article><span>Éliminations</span><strong>{activeReport.overview.player_kills}</strong></article>
              <article><span>Morts</span><strong>{activeReport.overview.player_deaths}</strong></article>
              <article><span>HP reçus</span><strong>{activeReport.overview.damage_received}</strong></article>
            </section>

            <div className="report-grid">
              <section className="panel panel--timeline">
                <div className="panel-heading">
                  <div><p className="eyebrow">Contexte</p><h2>Timeline</h2></div>
                  {isRoundLoading && <span className="loading-label">Mise à jour…</span>}
                </div>
                <div className="round-strip" aria-label="Filtrer par round">
                  <Button className={`round-button ${activeReport.selectedRound === undefined ? "is-selected" : ""}`} onPress={() => void selectRound(undefined)}>Tous</Button>
                  {roundNumbers.map((roundNumber) => (
                    <Button
                      aria-label={displayRound(roundNumber)}
                      className={`round-button ${activeReport.selectedRound === roundNumber ? "is-selected" : ""}`}
                      key={roundNumber}
                      onPress={() => void selectRound(roundNumber)}
                    >
                      {roundNumber + 1}
                    </Button>
                  ))}
                </div>
                <Timeline events={activeReport.timeline} playerId={activeReport.overview.selected_player.id} />
              </section>

              <section className="panel panel--zones">
                <div className="panel-heading">
                  <div><p className="eyebrow">H-04 · Confiance directe</p><h2>Où vous perdez des HP</h2></div>
                  <span className="grid-key">Grille monde</span>
                </div>
                <p className="panel-description">Chaque cellule agrège la position exacte de la victime au moment du dégât. Ce n’est pas encore un callout Mirage.</p>
                <DamageGrid cells={activeReport.damageCells} />
              </section>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
