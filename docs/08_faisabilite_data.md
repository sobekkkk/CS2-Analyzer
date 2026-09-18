# Faisabilite data - premier passage

Date de controle : 16 septembre 2026  
Parser controle : `demoparser2 0.42.0` (local, isole dans `.tools/python`)

## Verdict

**GO pour le MVP analytique Mirage.**

Les cinq demos du corpus sont des fichiers CS2 `PBDEMS2` lisibles. Elles couvrent deux builds de jeu (`14165`, `14174`) et chaque demo fournit 10 joueurs, morts, degats, bombes plantees et grenades lancees. Un test complet de ticks sur `vitality-vs-mouz-m1-mirage.dem` a aussi extrait 2 014 200 echantillons de joueur avec `X`, `Y`, `Z`, `health`, `is_alive`, `team_num`, `tick`, nom et SteamID.

## Inventaire facture

| Demo | Build | Morts | Degats | Plantes | Grenades |
| --- | ---: | ---: | ---: | ---: | ---: |
| MOUZ - Vitality M2 | 14174 | 143 | 527 | 11 | 368 |
| Vitality - Spirit M3 | 14174 | 101 | 415 | 8 | 339 |
| Vitality - Legacy M2 | 14174 | 161 | 582 | 9 | 444 |
| B8 - Vitality M1 | 14174 | 193 | 746 | 16 | 612 |
| Vitality - MOUZ M1 | 14165 | 147 | 565 | 13 | 448 |
| **Total** | - | **745** | **2 835** | **57** | **2 211** |

Les empreintes et chemins de chaque fichier figurent dans [`corpus/manifest.v0.yml`](corpus/manifest.v0.yml).

## Couverture des quatre analyses MVP

| Analyse | Faits necessaires | Etat |
| --- | --- | --- |
| H-01 morts sans trade | `player_death`, joueurs/equipes, positions et ticks | Donnees presentes ; regle et seuils a calibrer |
| H-02 position de premier kill | ordre des morts, killer/victime, position/tick | Donnees presentes |
| H-03 position en 5v4 | morts, equipe, etat vivant, positions | Donnees presentes |
| H-04 zones de HP perdus | `player_hurt`, victime, HP, position/tick | Donnees presentes |

## Ce que ce test ne prouve pas encore

- la justesse du mapping coordonnees monde -> image de Mirage ;
- l'identification fiable des callouts/nav areas ;
- la pertinence des seuils de trade et de distance ;
- une couverture pour les demos de joueurs ordinaires ou de futurs patches ;
- une reproduction de ce que le joueur voyait exactement a l'ecran.

## Etape suivante : oracle humain

Avant toute interface, remplir la [fiche golden](/C:/Users/drago/Documents/ChatGPT/CS2%20round%20analyzer_/docs/corpus/golden-sheet.template.md) sur une demo. Elle etablit les quelques faits controles manuellement contre lesquels nous testerons l'extraction automatique et les premieres regles.

