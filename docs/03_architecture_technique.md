# Architecture technique cible

## Decision de depart

Construire un prototype local en **Python 3.12 + demoparser2 + Awpy**, puis isoler le parsing derriere une interface interne. Ce choix donne un chemin court vers les evenements, positions, cartes et dataframes sans reecrire le protocole Source 2.

`demoparser2` fournit un coeur Rust interrogeable depuis Python/JavaScript et expose les evenements/ticks necessaires ; Awpy est une couche Python d'analytics et de visualisation CS2. Le parser demeure remplaçable si une version du jeu impose plus tard une autre implementation.

## Systeme d'interface : composants oui, theme pret-a-porter non

L'interface web utilisera **React Aria Components** comme fondation d'interaction : boutons, menus, listes, dialogues, selects, tableaux et raccourcis clavier accessibles. La bibliotheque est volontairement sans style impose ; notre design system CSS reste proprietaire au projet.

Cette decision evite les interfaces reconnaissables "template SaaS" tout en ne reinventant pas les comportements difficiles (focus, clavier, touch, lecteurs d'ecran). Nous ne partirons pas d'un kit visuel complet ni d'un theme shadcn copie-colle. Les quelques composants repetes (bouton, filtre, panneau de preuve, onglet de round, tooltip) seront definis dans le repository avec leurs propres tokens et leur propre rythme visuel.

Direction retenue pour le MVP : **dashboard classique et sobre**. Hierarchie simple, surfaces discretes, une couleur d'accent reservee aux elements actifs et signaux, typographie systeme lisible et donnees denses sans surcharge. Il ne cherchera ni l'esthetique neon esport, ni la mise en scene editoriale, ni le dashboard a cartes interchangeables.

## Architecture MVP

```text
.dem termine
  -> validation et empreinte SHA-256
  -> worker de parsing isole
  -> adaptateur Source2 -> modele canonique
  -> Parquet/DuckDB local
  -> moteur de regles deterministes
  -> API locale FastAPI
  -> interface web locale (React/TypeScript)
```

## Pourquoi cette separation

- Le format Valve evolue ; seul l'adaptateur connait les noms de champs du parser.
- L'interface et les regles ne dependent jamais directement de `m_iHealth`, etc.
- Les analyses sont recalculables et testables a partir d'un modele stable.
- Un fichier `.dem` est une entree non fiable : le worker peut etre limite et echouer sans tuer l'interface.

## Modele canonique minimal

| Objet | Champs indispensables |
| --- | --- |
| `Match` | id, map, tick_interval, parser_version, source_hash |
| `Round` | numero, start/end tick, winner, reason, score avant/apres |
| `Player` | internal_id, display_name, team par round |
| `Kill` | round, moment, killer, victim, weapon, position si disponible |
| `Damage` | round, moment, attacker, victim, hp_damage, weapon, position victime |
| `PlayerSample` | moment, player, xyz, alive, health, armor, weapon, team |
| `AdvantageWindow` | round, equipe, debut/fin, vivants T/CT |
| `Insight` | id, rule_version, confidence, evidence, recommendation |

Tous les objets temporels gardent `server_tick`, `subtick` quand disponible, `round` et la provenance.

## Persistance locale

```text
data/
  raw/<sha256>.dem                 # conserve seulement si l'utilisateur l'autorise
  matches/<match-id>/metadata.json
  matches/<match-id>/rounds.parquet
  matches/<match-id>/kills.parquet
  matches/<match-id>/damages.parquet
  matches/<match-id>/player_samples.parquet
  matches/<match-id>/insights.json
```

Parquet sert aux tables chronologiques ; DuckDB permet les requetes locales sans serveur de base de donnees. Ne pas enregistrer d'audio/voice, chat ou identifiant Steam brut dans le MVP.

## Contrats internes

```python
class DemoIngestor(Protocol):
    def inspect(path: Path) -> DemoMetadata: ...
    def parse(path: Path, selection: PlayerSelection) -> CanonicalMatch: ...

class InsightRule(Protocol):
    id: str
    version: str
    def evaluate(match: CanonicalMatch, player_id: str) -> list[Insight]: ...
```

Chaque regle recoit le meme modele canonique et produit des preuves structurees. Aucune phrase utilisateur ne doit etre la seule sortie de la regle.

## Securite et confidentialite par conception

- Taille maximale de demo, timeout et limite memoire du worker a definir avant exposure publique.
- Dossier de travail lecture seule pour le parser ; aucune sortie reseau du worker.
- Hash du fichier pour reproductibilite ; ne pas exposer l'identite Steam dans une URL ou un export par defaut.
- Aucun acces a `cs2.exe`, aucune injection, aucun service live dans le MVP.

## Evolution apres MVP

1. Plus de cartes et mapping callouts/nav.
2. Compte local puis synchronisation consentie.
3. Validation statistique des regles et personnalisation.
4. Backend event-driven/CSTV seulement si un cas tournoi autorise le justifie.
