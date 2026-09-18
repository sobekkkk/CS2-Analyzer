# PRD - MVP : debrief de demo actionnable

## Parcours utilisateur

1. Le joueur ouvre l'outil local et depose un fichier `.dem` termine.
2. L'outil verifie le format, affiche la carte, les joueurs detectes et demande de choisir le joueur analyse.
3. Il analyse la demo et montre une progression lisible ; une erreur explique ce qui manque si le fichier n'est pas supporte.
4. Le joueur arrive sur un rapport : score, stats principales, priorites, timeline par round et cartes contextuelles.
5. Il ouvre un constat pour voir la regle, les donnees prises en compte et les rounds associes.
6. Il exporte un rapport local HTML ou JSON (optionnel apres la V1 fonctionnelle).

## Ecrans minimaux

### 1. Import

- Zone de depot et selection de fichier.
- Etat : pret, en analyse, termine, erreur recuperable.
- Metadonnees lues : carte, duree, nombre de rounds, joueurs lorsque disponibles.

### 2. Vue d'ensemble

- Score final, cote T/CT et joueur cible.
- K/D/A, ADR, KAST, opening duels, utility damage, taux de trade.
- Trois a cinq opportunites de progression, triees par impact/repetition.
- Aucune note globale de "niveau" dans le MVP.

### 3. Timeline de match

- Un bloc par round : buy, premiers contacts, morts, plante/desamorcage, issue.
- Filtres : T/CT, round gagne/perdu, type de constat.
- Clic sur un evenement : zoom sur le segment et liens vers la demo/tick.

### 4. Cartes intelligentes

- Mort sans trade possible.
- Premier kill obtenu.
- Position pendant un 5v4 favorable.
- Degats recus, ponderes par HP perdus.

Chaque carte doit proposer filtres T/CT, round, arme si pertinent, et afficher `n` occurrences. Sans echantillon suffisant, elle indique "pas assez de donnees".

### 5. Detail d'une opportunite

- Enonce court, niveau de confiance et nombre de repetitions.
- Faits : round, timestamp, position/zone, coequipier pertinent, delai calcule.
- Explication de la regle et limites.
- Action recommande : une seule habitude mesurable.

## User stories et criteres d'acceptation

| ID | User story | Accepte lorsque |
| --- | --- | --- |
| US-01 | En tant que joueur, j'importe ma demo pour l'analyser. | Un fichier valide produit un match ; un fichier invalide renvoie une erreur utile sans fermer l'application. |
| US-02 | Je choisis mon joueur. | Les dix participants sont proposes ; le choix est conserve dans le rapport. |
| US-03 | Je comprends le resultat du match. | Score, equipes, rounds et stats de base concordent avec la demo CS2 sur le corpus de reference. |
| US-04 | Je trouve les positions problematiques. | Les 4 cartes sont filtrables, contextualisees et chaque point renvoie a au moins un round. |
| US-05 | Je comprends une alerte de coaching. | Chaque alerte expose la regle, les valeurs observees et au moins un exemple. |
| US-06 | Je peux contester/verifier le resultat. | L'outil conserve round, server tick et source des donnees pour chaque observation. |

## Exigences non fonctionnelles

- Application locale Windows en premier ; navigateur local acceptable.
- Une demo de match standard doit aboutir sans intervention manuelle autre que le choix du joueur.
- Le moteur n'envoie jamais de contenu de demo vers Internet dans le MVP.
- Les erreurs de parsing sont isolees du processus d'interface.
- Les calculs sont reproductibles : meme demo + meme version = meme resultat.
- L'interface ne promet pas de precision visuelle/frame-perfect.

## Metriques produit a instrumenter plus tard

- Taux d'analyses terminees.
- Duree import -> rapport.
- Nombre d'observations ouvertes par rapport.
- Utilite declaree par observation (utile / peu clair / faux contexte).
- Taux de retours faux-positifs par regle.

