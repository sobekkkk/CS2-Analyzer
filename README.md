# CS2 Round Analyzer - dossier de pre-lancement

Ce dossier fige les decisions de produit avant de commencer le code. Il est ecrit pour etre compris par une personne non-technique et assez precis pour alimenter une IA de developpement.

## Etat d'execution

- **Lots A1-A3 - socle de donnees : termines.** L'API inspecte une demo Mirage, exclut la phase knife, normalise rounds/kills/degats et ne sauvegarde que les tables derivees pseudonymisees.
- **Lot B1 - selection de joueur : termine.** Import temporaire, choix valide, profil local preselectionne puis suppression automatique de la demo brute.
- **Lot C3 - moteur H-02 : termine.** Les opening kills sont calcules avec preuve directe ; validation reelle sur la demo `xSobek` (3 occurrences).
- **Lot C5 - moteur H-04 : termine.** Les HP recus sont agreges par cellule monde a partir de la position victime directe ; validation reelle sur une demo FACEIT (588 dommages positionnes).
- **Lots B2-B3 - consultation API : termines.** Le recap, la timeline par round et les cellules H-04 sont exposes depuis les tables locales derivees.
- **Lot D1 - frontend alpha : en validation.** Le parcours import -> choix du joueur -> recap -> timeline -> heatmap est implemente et passe ses controles locaux ; il doit maintenant passer la CI et une revue visuelle avec les donnees reelles.
- Chaque lot doit rester petit, teste sur le corpus et documente avant de passer au suivant.

## La vision en une phrase

Transformer une demo CS2 terminee en un debrief individuel clair, actionnable et justifie : *ce qui s'est passe, ou, dans quel contexte, et quelle habitude tester a la prochaine partie*.

## Ordre de lecture

1. [Vision et cadrage](docs/00_vision_et_cadrage.md) - pourquoi le produit existe et pour qui.
2. [PRD du MVP](docs/01_prd_mvp.md) - ce que la premiere version doit faire.
3. [Regles analytics](docs/02_regles_analytics.md) - definitions calculables et langage de coaching.
4. [Architecture cible](docs/03_architecture_technique.md) - choix techniques, donnees et interfaces.
5. [Roadmap et backlog](docs/04_roadmap_et_backlog.md) - ordre de construction et criteres d'acceptation.
6. [Risques et validation](docs/05_risques_et_validation.md) - qualite, securite, legal et tests.
7. [Questions de lancement](docs/06_questions_de_lancement.md) - decisions a valider ensemble avant le premier commit.
8. [Politique IA locale](docs/07_ia_locale.md) - ou l'IA aide, et ou elle ne doit pas decider.
9. [Manifeste technique](docs/corpus/manifest.v0.yml) - demos professionnelles pour regression du parser.
10. [Manifeste corpus joueurs](docs/corpus/target-manifest.v0.yml) - 12 demos Mirage recentes pour calibrer sans norme professionnelle.
11. [Golden set analytique](docs/corpus/golden-sheet.v0.md) - 50 scenes de replay pseudonymisees a verifier avant implementation.
12. [Systeme de design](docs/09_design_system.md) - composants, comportements et direction visuelle valides.
13. [Plan de test UX](docs/10_plan_test_ux.md) - protocole de validation avec cinq joueurs.
14. [Specification de developpement](docs/11_specification_developpement.md) - contrat d'implementation du MVP.
15. [Contrat analytique](docs/12_contrat_analytique_v0.md) - definitions et seuils calibres des quatre analyses.
16. [Adaptateur de carte](docs/13_spec_adaptateur_carte.md) - contrat Mirage pour zones, radar et distances.
17. [Strategie de corpus joueurs](docs/14_strategie_corpus_joueurs.md) - collecte cible et recalibration des seuils.
18. [Go / no-go alpha](docs/15_go_no_go_alpha.md) - ce qui autorise le debut du code et ce qui reste reporte a la beta.
19. [Cadre de livraison](docs/16_cadre_de_livraison.md) - backlog, Definition of Done, tests, GitHub et metriques.
20. Le cycle de livraison applique le TDD : test qui echoue, implementation minimale, refactorisation, controles locaux puis CI verte avant fusion.

## Decision provisoire de produit

Le MVP est un outil **local, post-match et mono-utilisateur**. Il importe une demo `.dem`, analyse une partie competitive sur une carte prise en charge et produit :

- un recap de match et de rounds ;
- quatre heatmaps contextuelles ;
- des observations de coaching expliquees avec leur niveau de confiance ;
- une timeline et des liens vers les moments concernes.

Le live, le replay 3D, la video automatique, la voix, le classement public et une IA generative libre sont volontairement hors MVP.

## Regle de gestion du projet

Rien ne passe dans la colonne "a developper" sans :

1. une valeur claire pour le joueur ;
2. une definition mesurable ;
3. un exemple de demo permettant de verifier le resultat ;
4. un niveau de confiance et des limites explicites.
