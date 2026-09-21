# Contrat analytique v0 - calibration des quatre signaux

## Statut et principe

Ce document transforme les hypotheses de `02_regles_analytics.md` en calculs implementables. Les seuils sont centralises dans une configuration versionnee, jamais caches dans l'interface ou dans une requete SQL.

La calibration technique `provisional_technical` reposait sur cinq demos professionnelles Vitality/Mirage. Elle est conservee pour les tests de regression, mais ne sert plus de reference de coaching.

La reference de calibration v0 devient `player_mirage_v0` : 12 demos Mirage recentes fournies par le porteur du projet, reparties entre FACEIT 3, FACEIT 7, Premier 15--20k et FACEIT 10. Apres exclusion de la phase knife FACEIT, elles contiennent 1 710 morts eligibles pour le calcul de trade et 294 trades trouves dans la fenetre de 5 s. Le manifeste est `corpus/target-manifest.v0.yml`.

## Base temporelle

- Un `Moment` est un `server_tick` plus un `subtick` optionnel.
- Le corpus de reference avance a **64 ticks/s** : la difference de `game_time` entre deux ticks consecutifs est `0,015625 s`.
- L'implementation doit obtenir la cadence depuis la demo / le parser. Elle ne doit pas ecrire `64` en dur dans une regle.
- Toute fenetre temporelle est convertie au runtime : `max_tick_delta = seconds / tick_interval`.

## Exclusion pre-match / rounds knife

Les rounds knife ne sont jamais representatifs du produit et sont exclus de **tous** les signaux et de toutes les statistiques.

Une demo FACEIT peut reutiliser `total_rounds_played = 0` pour le round knife puis le pistol round. Il est donc interdit de supprimer simplement le round `0`.

Pour chaque demo :

1. trouver le premier `round_officially_ended` ;
2. avant ce tick, trouver le dernier `player_death` dont `weapon` commence par `knife` ;
3. prendre le premier `round_start` strictement apres cette mort comme `competitive_start_tick` ;
4. ignorer tout evenement dont `tick < competitive_start_tick`.

S'il n'existe pas de kill knife initial ou de borne fiable, `competitive_start_tick = 0` et la demo est marquee pour controle de regression. Cette regle a retire 62 morts de pre-match dans les neuf demos FACEIT et n'en retire aucune dans les trois demos Premier Sobek.

## Parametres versionnes

```yaml
analytics_rules:
  version: 0.1
  trade:
    immediate_seconds: 1.0
    timely_seconds: 3.0
    maximum_seconds: 5.0
    minimum_alive_teammates_before_death: 2
  five_v_four:
    sample_start_seconds: 1.0
    sample_end_seconds: 6.0
    sample_interval_seconds: 1.0
  zones:
    fallback_cell_size_world_units: 256
    minimum_occurrences_for_trend: 3
```

## H-01 - Mort sans trade

### Definition de trade

Soit une mort `D` : la victime `V` est tues par `K` au tick `t`.

Le premier evenement `E` qui verifie toutes les conditions suivantes est le trade de `D` :

```text
E.tick > t
E.tick <= t + maximum_seconds
E.user_steamid == K
E.attacker_team_num == V.team_num
E.attacker_steamid != V.steamid  # V est deja morte
```

Sont exclus : suicide, world damage sans killer identifie, team kill, warmup et evenement apres la fin logique du round.

La phase pre-match / knife definie plus haut est egalement exclue de cette regle.

### Classification

| Classe | Condition |
| --- | --- |
| `immediate_trade` | premier trade <= 1,0 s |
| `timely_trade` | > 1,0 s et <= 3,0 s |
| `late_trade` | > 3,0 s et <= 5,0 s |
| `untraded` | aucun trade eligible <= 5,0 s |

### Donnee de calibration joueurs v0

Les delais ci-dessous ne sont pas une note de qualite : ils decrivent la vitesse de reponse observee dans le premier corpus de joueurs. Le faible volume de chaque segment impose de ne pas encore personnaliser les seuils par elo.

| Segment | Matchs | Trades / morts eligibles a 5 s | Mediane | P75 | P90 |
| --- | ---: |
| FACEIT 3 | 4 | 104 / 571 (18,2 %) | 2,10 s | 3,51 s | 4,32 s |
| FACEIT 7 | 2 | 54 / 267 (20,2 %) | 1,96 s | 3,28 s | 4,61 s |
| Premier 15--20k | 3 | 43 / 365 (11,8 %) | 1,97 s | 3,45 s | 4,17 s |
| FACEIT 10 | 3 | 93 / 507 (18,3 %) | 1,89 s | 3,02 s | 3,97 s |
| **Total corpus joueurs** | **12** | **294 / 1 710 (17,2 %)** | **1,98 s** | **3,27 s** | **4,29 s** |

La frontiere `timely_trade = 3 s` reste une limite pedagogique, proche du P75 FACEIT 10 et legerement plus stricte que le P75 du corpus joueurs complet. Les 5 s servent uniquement a distinguer un trade tardif d'une absence de trade. Elle ne signifie pas qu'un trade a 4,8 s etait tactiquement bon.

Avant de figer la version 1.0, nous verifierons manuellement des cas limites dans le replay : au moins 20 trades et 10 non-trades repartis entre les segments. Tant que cette revue n'est pas faite, les libelles restent `provisional_player_calibrated` et ne declenchent pas de jugement automatique de "mauvaise decision".

### Sorties produit

- La heatmap "morts sans trade" inclut toute mort `untraded` avec au moins deux coequipiers vivants avant la mort.
- L'observation de coaching ajoute seulement : round, killer, position de mort, joueurs vivants et classification. Elle ne dit pas encore "tu etais isole".
- Une observation "exposition isolee" exige en plus un calcul de chemin/nav mesh valide ; elle reste hors v0.1.

### Implementation alpha

Le moteur ne produit aucun statut H-01 si la cadence de ticks est absente ou invalide. Pour la seule condition d'eligibilite de la carte, il calcule les coequipiers vivants avant la mort a partir du format competitif **5v5** et des morts deja observees dans le round ; cette disponibilite reste donc `inferred`. Une demo a effectif incomplet ou atypique doit etre revue avant toute restitution de coaching.

## H-02 - Position de premier kill

### Definition

Pour chaque round, retenir le premier `player_death` entre equipes opposees. Team kills, suicides et warmup sont exclus.

Si le killer est le joueur cible :

- utiliser `attacker_X`, `attacker_Y`, `attacker_Z` fournis au moment de l'evenement, si disponibles ;
- sinon prendre le dernier `PlayerSample` du killer dont le tick est inferieur ou egal au tick de mort et age de 2 ticks maximum ;
- sinon omettre l'occurrence et incrementer `insufficient_position`.

### Sorties produit

`opening_kill` contient round, moment, killer, victime, arme, equipe, position, zone/cellule et issue du round. Une tendance n'est formulee qu'a partir de trois occurrences.

## H-03 - Position en 5v4

### Definition

Apres chaque mort valide d'un round, compter les joueurs vivants de chaque equipe. Une fenetre est ouverte uniquement si l'etat devient exactement `5 vivants contre 4`.

```text
window.start = death.tick
window.end = min(next_player_death.tick, round_end.tick, start + 6 s)
samples = positions du joueur cible a +1 s, +2 s, ... +6 s
```

Un echantillon est accepte seulement si :

- le joueur cible appartient a l'equipe a 5 ;
- le 5v4 existe encore a ce tick ;
- le joueur cible est vivant ;
- sa position est fiable.

Ne pas assimiler 4v3, 3v2 ou une simple superiorite numerique a un 5v4 dans le MVP.

### Sorties produit

L'alpha actuel agrege les positions du joueur pendant ces fenetres ; les dommages recus et morts dans ces fenetres sont planifies mais ne sont pas encore restitues. Le texte reste descriptif et ne diagnostique aucune erreur de rotation avant la phase nav mesh.

## H-04 - Zones de HP perdus

### Definition

Pour chaque `player_hurt` recu par le joueur cible :

- ignorer les degats a soi-meme et les degats allies dans v0.1 ;
- utiliser `dmg_health > 0` ;
- utiliser `user_X`, `user_Y`, `user_Z` au moment de l'evenement quand disponibles ;
- sinon prendre le dernier `PlayerSample` de la victime, age maximal de 2 ticks ;
- rattacher round, cote, arme attaquante, position et zone/cellule.

Deux agregats sont obligatoires : `hp_lost_total` et `hp_lost_per_passage`. Afficher `occurrences` et `passages` pour eviter qu'une seule rafale devienne artificiellement une tendance.

## Zones et carte Mirage

v0.1 adopte deux niveaux, jamais melanges :

1. `nav_place_name` : callout issu d'une source nav mesh/ressource de carte versionnee.
2. `fallback_cell_id` : grille monde de 256 unites, utilisee si aucun callout fiable n'est disponible.

Le front indique clairement "zone de grille" dans le second cas. Il ne doit jamais inventer le nom d'un callout a partir de coordonnees non mappees.

La transformation monde -> radar est un adaptateur `de_mirage` versionne et teste sur points connus. Elle n'entre dans aucun moteur de regles : elle sert seulement a l'affichage 2D.

## Confiance et donnees insuffisantes

| Niveau | Quand l'utiliser |
| --- | --- |
| `direct` | evenement ou champ de demo explicite, par exemple dommage et arme |
| `inferred` | resultat d'une sequence/fenetre, par exemple trade ou 5v4 |
| `insufficient_data` | champ requis absent ou position trop ancienne ; aucune insight n'est creee |

Chaque insight stocke `rule_version`, parametres appliques et `evidence` structuree. Dans l'alpha, chaque preuve contient au minimum `{round_number, tick, kind}` ; `kind` vaut `kill`, `damage` ou `position_sample`. Une interface peut donc ouvrir le bon round sans tenter de deduire un fait depuis un libelle.

## Cas de test a fixer dans le corpus golden

Avant implementation definitive, choisir et etiqueter manuellement :

- 5 trades immediats ou rapides ;
- 3 trades tardifs ;
- 5 morts sans trade ;
- 5 opening kills (au moins deux pour le joueur cible) ;
- 3 fenetres 5v4 avec changement d'etat ;
- 5 evenements `player_hurt` dans au moins trois zones.

Chaque cas garde fichier SHA-256, round, tick, joueurs, resultat attendu et une note de verification replay.
