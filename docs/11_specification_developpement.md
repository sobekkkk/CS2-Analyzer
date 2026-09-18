# Specification de developpement - MVP v0.1

## But de cette specification

Ce document donne a une IA ou un developpeur un contrat suffisamment precis pour construire le premier prototype sans inventer de fonctionnalites ni de regles de coaching.

Il ne remplace pas les documents produit :

- `01_prd_mvp.md` definit l'experience attendue ;
- `02_regles_analytics.md` definit les calculs ;
- `09_design_system.md` definit la forme et les interactions ;
- ce document definit ce qui doit etre construit et teste.

## Perimetre executable

### Inclus

- Application locale Windows, utilisable depuis un navigateur local.
- Import d'une demo `.dem` terminee.
- Selection d'un joueur parmi les participants reconnus.
- Analyse de `de_mirage` uniquement.
- Vue d'ensemble, timeline et analyse par zones.
- Quatre analyses : H-01 a H-04 de `02_regles_analytics.md`.
- Donnees locales et export JSON du rapport.

### Exclu

- Authentification, cloud, paiement et partage social.
- Parsing live / CSTV.
- Replay 3D, rendu video, capture CS2, audio, voice ou chat.
- IA generative en dependance de fonctionnement.
- Regles de crosshair, visibilite ou intention tactique.

## Choix de stack

| Couche | Choix | Responsabilite |
| --- | --- | --- |
| Runtime data | Python 3.12 | orchestration, schemas, calculs |
| Parsing | `demoparser2` 0.42+ | evenements et ticks CS2 |
| Geometrie Mirage | `Awpy` 2.0.2+ | nav mesh, distances et adaptateur de carte |
| API locale | FastAPI + Pydantic | validation, jobs et contrat HTTP |
| Stockage analytique | Parquet + DuckDB | tables locales derivees |
| Interface | React + TypeScript + Vite | ecrans et interactions |
| Composants | React Aria Components | comportement accessible sans theme impose |
| Styles | CSS modules/tokens locaux | design defini dans `09_design_system.md` |
| Tests Python | pytest | regles, normalisation, API |
| Tests UI | Vitest + Playwright | composants et parcours critiques |

Le front ne lit jamais directement une demo et ne depend jamais des noms internes Source 2. Il consomme uniquement le contrat HTTP stable ci-dessous.

## Arborescence cible

```text
cs2-round-analyzer/
  apps/
    api/
      app/
        adapters/       # demoparser2 -> modele canonique
        domain/         # schemas et regles H-01..H-04
        services/       # jobs, persistance, exports
        api/            # routes FastAPI
      tests/
    web/
      src/
        features/       # import, overview, timeline, zones
        components/     # composants UI projet
        api/            # client HTTP type
        styles/
      tests/
  contracts/
    openapi/            # export OpenAPI fige en CI
  fixtures/
    manifests/          # hashes et attentes golden, jamais les .dem publics
  docs/
```

Les fichiers `.dem`, donnees analysees et environnements locaux sont ignores par Git.

## Etats de traitement

```text
UPLOADED -> INSPECTING -> AWAITING_PLAYER -> PARSING -> ANALYZING -> READY
                                               |             |
                                               +-> FAILED <---+
```

- `UPLOADED` : fichier accepte temporairement.
- `INSPECTING` : signature, taille, hash, map et participants sont lus.
- `AWAITING_PLAYER` : le front affiche les participants de la demo sous forme de liste cliquable. L'utilisateur choisit son pseudo une seule fois ; son identifiant local est ensuite propose automatiquement pour les imports suivants.
- `PARSING` : extraction canonique en worker isole.
- `ANALYZING` : calcul des regles et agregats.
- `READY` : rapport consultable.
- `FAILED` : erreur structuree sans crash d'interface.

## Modele de donnees canonique

Les schemas exacts seront des modeles Pydantic versionnes. Les champs ci-dessous sont obligatoires au MVP.

### `Match`

```json
{
  "id": "match_01J...",
  "source_sha256": "...",
  "map": "de_mirage",
  "cs2_patch_version": "14174",
  "parser_version": "0.42.0",
  "tick_interval": 0.015625,
  "competitive_start_tick": 2469,
  "status": "ready"
}
```

### `Moment`

```json
{
  "server_tick": 38821,
  "subtick": null,
  "round_number": 18
}
```

`server_tick` est obligatoire ; `subtick` reste nullable si le parser ne fournit pas une valeur fiable.

### `Insight`

```json
{
  "id": "insight_h01_0007",
  "rule_id": "H-01",
  "rule_version": "0.1",
  "kind": "untraded_death",
  "confidence": "inferred",
  "severity": "review",
  "title": "Mort sans trade estime",
  "round_number": 18,
  "moment": { "server_tick": 38821, "subtick": null, "round_number": 18 },
  "zone": "Connector",
  "evidence": {
    "trade_window_seconds": 5,
    "trade_observed": false,
    "nearest_teammate_eta_seconds": 3.1,
    "alive_teammates_before_death": 3
  },
  "recommendation_key": "h01_synchronize_entry"
}
```

Le front traduit `recommendation_key` via une table locale. Il ne doit pas construire un conseil a partir d'un texte libre provenant du backend.

## API locale v1

| Methode | Route | Reponse / intention |
| --- | --- | --- |
| `POST` | `/api/v1/demos` | Accepte `.dem`, cree une analyse en etat `INSPECTING` |
| `GET` | `/api/v1/analyses/{id}` | Etat de job, erreurs structurees, progression |
| `POST` | `/api/v1/analyses/{id}/player` | Enregistre le joueur choisi depuis la liste de participants et lance le parsing |
| `GET` | `/api/v1/matches/{id}/overview` | Match, stats, insights prioritaires |
| `GET` | `/api/v1/matches/{id}/timeline?round=18` | Evenements et contexte du round |
| `GET` | `/api/v1/matches/{id}/zones?metric=hp_lost&side=all` | Agregats de zones et occurrences sources |
| `GET` | `/api/v1/matches/{id}/highlights/opening-kills` | Premiers kills ennemis du joueur, un par round, avec tick et arme source |
| `GET` | `/api/v1/matches/{id}/insights/{insight_id}` | Preuves d'une observation |
| `GET` | `/api/v1/matches/{id}/export` | Rapport JSON versionne |
| `DELETE` | `/api/v1/matches/{id}` | Supprime donnees locales du match |

Toutes les erreurs utilisent ce format :

```json
{
  "code": "unsupported_map",
  "message": "Cette version pilote ne prend en charge que de_mirage.",
  "details": { "map": "de_inferno" }
}
```

## Regles d'implementation critiques

1. Le parser s'execute dans un processus worker distinct de l'API.
2. Limiter taille de fichier, duree et memoire du worker avant d'exposer l'import a d'autres utilisateurs.
3. Stocker hash, version du parser et version de chaque regle sur chaque rapport.
4. N'echantillonner les positions qu'a la precision utile aux analyses ; ne pas dupliquer sans raison un objet joueur complet a chaque tick.
5. Une regle produit des donnees de preuve structurees avant de produire un titre.
6. Une absence de donnee donne `insufficient_data`, jamais une inference implicite.
7. Aucun SteamID brut n'est expose dans l'interface ou les exports par defaut.
8. Toute regle commence apres `competitive_start_tick` ; les rounds knife et la phase pre-match sont exclus selon `12_contrat_analytique_v0.md`.

## Criteres d'acceptation par lot

### Lot 1 - Ingestion fiable

- Les 5 demos techniques et les 12 demos joueurs du corpus golden sont inspectees sans crash.
- Carte, version de patch, participants, morts et degats sont lus ; une demo peut contenir 11 participants en cas de remplacement.
- Une demo invalide/tronquee renvoie une erreur comprehensible.

### Lot 2 - Modele et rapport

- Le score, le nombre de rounds et le nombre de morts correspondent aux attentes golden.
- Le joueur est choisi par un clic dans la liste issue de la demo, jamais par saisie d'un identifiant. Un profil local deja choisi est preselectionne lors de l'import suivant.
- Le rapport se recharge a l'identique depuis les donnees locales.

### Lot 3 - Analyses H-02 et H-04

- Les opening kills et pertes de HP renvoient round, tick et zone source.
- Les zones affichent toujours le nombre d'occurrences `n`.

### Lot 4 - Analyses H-01 et H-03

- Chaque signal de trade ou de 5v4 rend sa formule et ses variables visibles.
- Aucun signal n'est visible sans niveau de confiance.

### Lot 5 - UX et robustesse

- Les ecrans suivent `09_design_system.md`.
- Le parcours observation -> round -> evenement -> zone fonctionne au clavier.
- `Voir la preuve` ouvre directement le bon round, le bon moment et le joueur concerne ; aucune recherche manuelle de joueur n'est necessaire.
- La suppression locale d'un match retire aussi ses tables derivees.

## Definition of done du MVP

Le MVP est pret pour une beta privee lorsque :

- tous les lots ci-dessus passent sur le corpus golden ;
- les cinq tests UX ont ete menes ou explicitement reportes avec risque accepte ;
- aucun fichier demo ne quitte la machine sans action explicite de l'utilisateur ;
- les limites connues sont visibles dans l'interface et la documentation ;
- les resultats sont reproductibles avec la meme demo et les memes versions.
