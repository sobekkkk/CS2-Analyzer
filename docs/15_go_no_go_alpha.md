# Go / no-go - lancement de l'alpha local

## Decision

**GO pour demarrer le code de l'alpha local Mirage.**

Le perimetre est assez precis pour qu'un developpeur ou une IA implemente sans inventer les regles : import local, selection simple du joueur, timeline, quatre signaux, grille spatiale et preuves structurees.

Cette decision n'autorise pas encore une beta partagee ni une distribution publique.

## Etat des prealables

| Domaine | Etat alpha | Decision |
| --- | --- | --- |
| Probleme et cible | Pret | Joueur regulier, analyse post-match locale |
| MVP | Pret | Mirage, import `.dem`, quatre signaux H-01 a H-04 |
| Design | Pret | Dashboard sombre, sobre, composants accessibles personnalises |
| Faisabilite demo | Pret | 17 demos valides ; evenements et positions disponibles |
| Corpus joueurs | Pret | 12 demos recentes, 4 niveaux ; calibration sans norme pro |
| Rounds knife | Pret | Exclusion `competitive_start_tick` definie et calibree |
| Tests analytiques | Pret pour code | 50 fixtures automatiques ; revue visuelle reportee |
| Carte | Pret pour alpha | Grille spatiale explicite ; radar/callouts reportes beta |
| IA | Hors alpha | Regles explicables, sans API payante |
| Vie privee | Pret | Local par defaut, SteamID non expose, suppression locale |

## Ce que l'alpha doit livrer

1. Importer une demo Mirage locale et verifier son integrite.
2. Proposer les participants sous forme de liste ; retenir localement le choix de l'utilisateur.
3. Produire les faits de match, rounds, morts et dommages hors phase knife.
4. Afficher H-01 a H-04 sur une grille spatiale, toujours avec nombre d'occurrences et lien vers les incidents sources.
5. Permettre le parcours observation -> round -> evenement -> preuve sans demander de saisir ou retrouver un identifiant.
6. Executer le golden set de 50 cas a chaque changement de regle.

## Ce qui reste volontairement apres l'alpha

- Radar Mirage reel, callouts et nav mesh valides ; necessaires avant beta privee.
- Revue visuelle de quelques preuves directement depuis l'interface.
- Test UX avec cinq joueurs.
- Nouvelle carte, telechargement automatique de demos, IA locale de reformulation, coaching avance et distribution publique.

## Conditions pour passer en beta privee

- les 50 fixtures analytiques passent ;
- la fonction `Voir la preuve` selectionne automatiquement contexte et joueur ;
- 12/12 points de carte valident la transformation radar/callouts ;
- cinq joueurs ont realise le test UX ou le risque a ete explicitement accepte ;
- aucune demo ne sort de la machine sans action explicite.
