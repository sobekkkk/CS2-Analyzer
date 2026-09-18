# Golden set v0 - tests analytiques Mirage

## Methode simple

Tu n'as rien a rechercher dans un replay ni aucun joueur a identifier a la main. Cette feuille est un jeu de **tests automatiques** pour le futur moteur : chaque ligne donne le fichier, le round et le tick auxquels le resultat doit etre retrouve. Les noms et SteamID ne font pas partie du test.

Au moment du code, le test ouvre la demo, applique l'exclusion de phase knife, puis verifie le signal attendu au tick indique. Un echec bloque la livraison de la regle concernee.

La revue humaine est repoussee au premier prototype : l'interface devra avoir un bouton `Voir la preuve` qui selectionne automatiquement le joueur concerne, le round et une fenetre de huit secondes. C'est seulement a ce moment que nous verifierons visuellement quelques scenes, sans navigation ou recherche manuelle.

## Garde-fou knife

Avant toute recherche de cas, le moteur calcule `competitive_start_tick` selon la regle du [contrat analytique](../12_contrat_analytique_v0.md#exclusion-pre-match--rounds-knife). Les scenes ci-dessous sont toutes posterieures a cette borne. Les 62 morts de phase knife relevees dans les demos FACEIT ne sont donc pas presentes.

## Cas automatiques

| ID | Signal | Segment | Fichier | Round | Tick | Resultat attendu |
| --- | --- | --- | --- | ---: | ---: | --- |
| G01 | trade | faceit_3 | faceit-3-1 | 6 | 47261 | immediate_trade (0.141 s) |
| G02 | trade | faceit_7 | faceit-7-1300elo1 | 0 | 12503 | immediate_trade (0.203 s) |
| G03 | trade | premier_15_20k | premier-sobek-game1 | 9 | 69146 | immediate_trade (0.391 s) |
| G04 | trade | faceit_10 | faceit-10-2000elo | 0 | 6773 | immediate_trade (0.422 s) |
| G05 | trade | faceit_3 | faceit-3-2 | 0 | 6341 | immediate_trade (0.234 s) |
| G06 | trade | faceit_7 | faceit-7-1300elo2 | 1 | 10240 | immediate_trade (0.953 s) |
| G07 | trade | premier_15_20k | premier-sobek-game2 | 0 | 4115 | immediate_trade (1.000 s) |
| G08 | trade | faceit_10 | faceit-10-2000elo-2 | 1 | 12760 | immediate_trade (0.156 s) |
| G09 | trade | faceit_3 | faceit-3-1 | 6 | 47868 | timely_trade (2.781 s) |
| G10 | trade | faceit_7 | faceit-7-1300elo1 | 0 | 10767 | timely_trade (2.812 s) |
| G11 | trade | premier_15_20k | premier-sobek-game1 | 4 | 36268 | timely_trade (1.422 s) |
| G12 | trade | faceit_10 | faceit-10-2000elo | 0 | 6902 | timely_trade (1.516 s) |
| G13 | trade | faceit_3 | faceit-3-2 | 3 | 22182 | timely_trade (2.531 s) |
| G14 | trade | faceit_7 | faceit-7-1300elo2 | 0 | 5646 | timely_trade (2.984 s) |
| G15 | trade | premier_15_20k | premier-sobek-game2 | 2 | 17659 | timely_trade (1.469 s) |
| G16 | trade | faceit_10 | faceit-10-2000elo-2 | 2 | 16330 | timely_trade (1.797 s) |
| G17 | trade | faceit_3 | faceit-3-3 | 1 | 10613 | timely_trade (2.250 s) |
| G18 | trade | faceit_7 | faceit-7-1300elo1 | 0 | 12363 | timely_trade (2.188 s) |
| G19 | trade | faceit_3 | faceit-3-1 | 9 | 67875 | late_trade (3.016 s) |
| G20 | trade | faceit_7 | faceit-7-1300elo1 | 3 | 27727 | late_trade (3.688 s) |
| G21 | untraded | faceit_3 | faceit-3-1 | 0 | 5868 | untraded; morts equipe avant: 0 |
| G22 | untraded | faceit_7 | faceit-7-1300elo1 | 0 | 10947 | untraded; morts equipe avant: 0 |
| G23 | untraded | premier_15_20k | premier-sobek-game1 | 0 | 2549 | untraded; morts equipe avant: 0 |
| G24 | untraded | faceit_10 | faceit-10-2000elo | 0 | 5494 | untraded; morts equipe avant: 0 |
| G25 | untraded | faceit_3 | faceit-3-2 | 0 | 5511 | untraded; morts equipe avant: 0 |
| G26 | untraded | faceit_7 | faceit-7-1300elo2 | 0 | 5099 | untraded; morts equipe avant: 0 |
| G27 | untraded | premier_15_20k | premier-sobek-game2 | 0 | 3775 | untraded; morts equipe avant: 0 |
| G28 | untraded | faceit_10 | faceit-10-2000elo-2 | 0 | 5310 | untraded; morts equipe avant: 0 |
| G29 | untraded | faceit_3 | faceit-3-3 | 0 | 6224 | untraded; morts equipe avant: 0 |
| G30 | untraded | faceit_7 | faceit-7-1300elo1 | 0 | 11041 | untraded; morts equipe avant: 1 |
| G31 | opening_kill | faceit_3 | faceit-3-1 | 0 | 5868 | premier kill inter-equipes du round |
| G32 | opening_kill | faceit_7 | faceit-7-1300elo1 | 0 | 10767 | premier kill inter-equipes du round |
| G33 | opening_kill | premier_15_20k | premier-sobek-game1 | 0 | 2549 | premier kill inter-equipes du round |
| G34 | opening_kill | faceit_10 | faceit-10-2000elo | 0 | 5494 | premier kill inter-equipes du round |
| G35 | opening_kill | faceit_3 | faceit-3-2 | 0 | 5511 | premier kill inter-equipes du round |
| G36 | opening_kill | faceit_7 | faceit-7-1300elo2 | 0 | 5099 | premier kill inter-equipes du round |
| G37 | opening_kill | premier_15_20k | premier-sobek-game2 | 0 | 3775 | premier kill inter-equipes du round |
| G38 | opening_kill | faceit_10 | faceit-10-2000elo-2 | 0 | 5310 | premier kill inter-equipes du round |
| G39 | opening_kill | faceit_3 | faceit-3-3 | 0 | 6224 | premier kill inter-equipes du round |
| G40 | opening_kill | faceit_7 | faceit-7-1300elo1 | 1 | 15500 | premier kill inter-equipes du round |
| G41 | five_v_four | faceit_3 | faceit-3-1 | 0 | 5868 | ouverture 5v4; equipe 3 en avantage |
| G42 | five_v_four | faceit_7 | faceit-7-1300elo1 | 0 | 10767 | ouverture 5v4; equipe 2 en avantage |
| G43 | five_v_four | premier_15_20k | premier-sobek-game1 | 0 | 2549 | ouverture 5v4; equipe 3 en avantage |
| G44 | five_v_four | faceit_10 | faceit-10-2000elo | 0 | 5494 | ouverture 5v4; equipe 2 en avantage |
| G45 | five_v_four | faceit_3 | faceit-3-2 | 0 | 5511 | ouverture 5v4; equipe 3 en avantage |
| G46 | hp_lost | faceit_3 | faceit-3-1 | 0 | 5683 | degats HP 71; position a resoudre au tick |
| G47 | hp_lost | faceit_7 | faceit-7-1300elo1 | 0 | 10732 | degats HP 5; position a resoudre au tick |
| G48 | hp_lost | premier_15_20k | premier-sobek-game1 | 0 | 2549 | degats HP 119; position a resoudre au tick |
| G49 | hp_lost | faceit_10 | faceit-10-2000elo | 0 | 5483 | degats HP 89; position a resoudre au tick |
| G50 | hp_lost | faceit_3 | faceit-3-2 | 0 | 5505 | degats HP 2; position a resoudre au tick |

## Critere de passage

Les 50 cas doivent passer dans la suite de tests. La future interface devra aussi presenter une preuve navigable automatiquement pour au moins un cas de chaque signal. Aucun critere ne demande a un testeur de retrouver un joueur inconnu.
