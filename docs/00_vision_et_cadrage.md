# Vision et cadrage

## Probleme a resoudre

Les statistiques CS2 classiques disent surtout *combien* un joueur a fait de kills ou de degats. Elles expliquent peu *pourquoi* un duel a ete perdu, si un coequipier pouvait trader, si le timing etait mauvais, ou si la position etait recurrente et risquee.

Le produit doit aider un joueur amateur ou competitif a progresser apres une partie sans lui demander de revoir quarante minutes de demo.

## Utilisateur initial

**Joueur CS2 regulier, niveau Premier/Faceit, qui analyse ses propres demos.** Il comprend les notions de trade, entry, eco et reprise de site, mais ne veut ni tableur ni jargon de data science.c

Le coach, l'equipe et le createur de contenu sont des profils futurs, pas des cibles du premier lancement.

## Proposition de valeur

En moins de deux minutes apres l'import d'une demo, le joueur obtient :

> Trois a cinq constats prioritaires, chacun relie a un ou plusieurs rounds, avec une explication factuelle et une piste concrete a tester.

Exemple : "Round 18 : tu es mort seul en B. Le coequipier le plus proche ne pouvait pas te trade avant 3,1 s. Avant de reprendre ce duel, attends le contact de ton mate ou demande un flash."

## Principes produit

- **Action avant volume.** Cinq retours utiles valent mieux que cinquante cartes.
- **Explicable avant intelligent.** Toute alerte doit montrer les faits et sa regle.
- **Humilite.** Le produit dit "signal a verifier", pas "mauvaise decision" lorsque les donnees ne permettent pas un verdict fiable.
- **Contexte.** Une position n'est jamais analysee sans phase du round, avantage numerique, equipe et objectif.
- **Post-match et hors jeu.** Aucun hook, injection ou interaction avec le processus CS2.
- **Vie privee par defaut.** Analyse locale, aucune voix, aucun partage public dans le MVP.

## Perimetre MVP

| Inclus | Exclu volontairement |
| --- | --- |
| Import d'une demo terminee | Analyse live pendant une partie |
| Une carte pilote (de_mirage) | Toutes les cartes au jour 1 |
| Joueur selectionne parmi les 10 joueurs | Identification Steam automatique parfaite |
| Timeline, recap, statistiques utiles | Replay 3D ou rendu pixel-perfect |
| 4 heatmaps contextuelles | Heatmap decorative sans question produit |
| Regles deterministes de coaching | LLM qui invente un diagnostic |
| Export local d'un rapport | Comptes, paiement, partage social |

## Ce que veut dire "mauvaise decision"

Ce n'est pas une verite objective. Dans le MVP, le terme visible sera **"opportunite de progression"**. Elle est emise seulement si :

1. la demo fournit les faits necessaires ;
2. une regle claire est satisfaite ;
3. le contexte est assez stable ;
4. le message propose une action testable.

Les jugements qui exigent la vision exacte du joueur, ses communications, son intention ou une reconstitution image-par-image ne seront pas automatises au debut.

## Objectifs de succes du prototype

- Une demo competitive valide est analysee de bout en bout sans crash.
- Le joueur retrouve chaque observation dans la timeline et peut constater les faits sources.
- Au moins 70 % des observations testees sur un petit panel sont jugees "compréhensibles et utiles".
- Aucun resultat n'est presente comme certain si le signal est seulement infere.

## Anti-objectifs

- Construire un clone de Leetify/Scope.gg avant d'avoir valide une fonctionnalite distincte.
- Ecrire un parser Source 2 maison.
- Stocker toutes les positions de tous les joueurs a chaque tick sans besoin analytique.
- Promettre une lecture exacte de ce que le joueur voyait a l'ecran.

