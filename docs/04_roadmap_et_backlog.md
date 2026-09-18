# Roadmap et backlog de pre-lancement

## Jalons : on ne code pas encore

| Jalon | Livrable | Porte de sortie |
| --- | --- | --- |
| M0 - Cadrage | Documents 00 a 06 valides | Cible, promesse et MVP acceptes |
| M1 - Faisabilite data | 10 demos etiquetees + inventaire des champs | Les donnees requises existent sur le corpus |
| M2 - UX testable | Wireframes cliquables + 5 retours joueurs | Les ecrans sont compris sans explication du createur |
| M3 - Spec developpeur | Contrats, schemas, criteres d'acceptation, corpus de test | Une IA/dev peut implementer sans deviner les regles |
| M4 - Lancement code | Backlog priorise, risques ouverts assignes | Go explicite |

## Backlog MVP par epics

## Etat UX - 16 septembre 2026

- Direction visuelle validee en interne : dashboard sombre, classique et sobre.
- Parcours "observation -> round -> evenement -> zone" valide en maquette.
- Reste a faire avant la sortie du jalon M2 : recueillir cinq retours de joueurs sur la comprehension de ces deux ecrans.

Le contrat complet est dans [`09_design_system.md`](09_design_system.md).

## Decision carte - 18 septembre 2026

- Les analyses Mirage, la timeline et les heatmaps peuvent avancer tout de suite avec une grille spatiale clairement nommee.
- Le vrai radar et les callouts sont une porte de sortie pour la beta privee, pas un prealable a l'alpha.
- La tentative de recuperation des assets `maps/navs` Awpy a echoue (miroir 404). Aucun asset non verifie ne sera integre ni redistribue.

### EPIC A - Import et modele de match

- A1. Verifier la signature, la taille et les metadonnees d'une demo. **Termine le 18 septembre 2026** : API locale et test reel FACEIT, y compris exclusion du round knife.
- A2. Generer `match_id`, hash, version de parser et journal d'analyse. **Termine le 18 septembre 2026** : identifiant derive du hash, manifest local et aucune copie de `.dem`.
- A3. Normaliser rounds, joueurs, kills et dommages. **Termine le 18 septembre 2026** : tables Parquet pseudonymisees validees sur une demo FACEIT.
- A4. Echantillonner les positions sans dupliquer inutilement chaque tick.

**Definition of done :** sur 10 demos de reference, rounds, score final et kill count concordent avec la lecture CS2 ou une reference independante.

### EPIC B - Rapport de base

- B1. Selection du joueur cible. **Termine le 18 septembre 2026** : staging temporaire, choix controle, profil local et suppression de la demo apres analyse.
- B2. Recap score/equipes/statistiques. **Termine le 18 septembre 2026** : recap local pseudonymise (rounds, K/D, HP recus) expose par API.
- B3. Timeline filtrable par round. **Termine le 18 septembre 2026** : faits de degats et morts tries au tick, avec filtre de round et test de contrat API.
- B4. Gestion d'erreurs lisible.

**Definition of done :** un testeur retrouve la mort citee par une observation en moins de 30 secondes.

### EPIC C - Heatmaps contextuelles

- C1. Transformation coordonnees monde -> carte 2D pour de_mirage.
- C2. H-01 morts sans trade. **Moteur, API et restitution alpha termines le 18 septembre 2026** : classification temporelle explicable (immediate, timely, late, untraded), carte de grille limitee aux morts non tradees avec au moins deux coequipiers vivants avant la mort, et lien vers les ticks sources. Le rendu rappelle explicitement qu'il ne prouve ni ligne de vue ni mauvaise decision.
- C3. H-02 premiers kills. **Moteur termine le 18 septembre 2026** : team-kills exclus, preuve directe, validation sur la demo `xSobek`.
- C4. H-03 fenetres 5v4.
- C5. H-04 degats recus. **Moteur et API termines le 18 septembre 2026** : HP recus agreges par cellule monde, position victime directe et liens vers les rounds sources. Le rendu carte reste a faire.

**Definition of done :** chaque point agregé expose son nombre d'occurrences et des liens vers les incidents sources.

### EPIC D - Coaching explicable

- D1. Format d'evidence commun pour une `Insight`.
- D2. Scoring impact x repetition x confiance.
- D3. Vue detail et recommandation courte.
- D4. Libelle "signal a verifier" si la confiance est inferee.

**Definition of done :** aucune insight ne peut etre affichee sans round, moment, regle et preuve associes.

### EPIC E - Qualite et livraison locale

- E1. Corpus golden et tests de non-regression.
- E2. Tests differentiels avec une seconde implementation quand possible.
- E3. Packaging Windows et guide utilisateur.
- E4. Telemetrie locale opt-in des faux positifs (si ajoutee).

**Definition of done :** l'outil est installable, analysable hors-ligne et ses donnees locales peuvent etre supprimees.

## Ordre de construction quand le code commencera

1. A1-A3 : importer une demo et rendre les faits fiables.
2. B1-B4 : rendre ces faits consultables.
3. C1, H-02, H-04 : visualisations a faible ambiguité.
4. H-01 et H-03 : regles temporelles/contextuelles.
5. D1-D4 : prioriser et expliquer sans survendre.
6. E1-E4 : durcir, tester et packager.

## Ce qui n'entre qu'apres validation

- Analyse d'eco complexe, timings de reprise, flanks et visibilite.
- Multi-cartes.
- Comparaison avec ses anciennes parties.
- ML/recommandations personnalisees.
- Live CSTV, overlays et highlights video.
