# Plan de test UX - MVP

## Objectif

Verifier que des joueurs CS2 comprennent le produit sans explication du createur, et qu'ils peuvent suivre une observation jusqu'a ses preuves.

Ce test ne mesure pas encore la precision des algorithmes ; il mesure la clarte de l'interface et du langage.

## Participants

Recruter cinq joueurs qui jouent au moins une fois par semaine. Viser si possible des profils differents :

- 2 joueurs Premier/Matchmaking reguliers ;
- 2 joueurs FACEIT ou equipe amateur ;
- 1 joueur qui ne regarde presque jamais ses demos.

Ne pas tester uniquement des amis deja impliques dans le projet : ils connaissent trop bien l'intention.

## Materiel

- Maquette Vue d'ensemble validee.
- Maquette Timeline et zones validee.
- Un lien/affichage de la demo d'exemple, seulement si le participant demande a verifier un round.
- La fiche de prise de notes ci-dessous.

## Deroule - 20 minutes par joueur

### Introduction - 2 min

Dire :

> Tu testes une maquette d'outil d'analyse CS2. Il n'y a pas de mauvaise reponse : c'est l'interface que nous evaluons. Pense a voix haute et dis ce qui te semble flou.

Ne pas expliquer les termes de l'interface avant les taches.

### Tache 1 - comprendre le rapport - 4 min

Afficher la Vue d'ensemble.

Demander :

> Quel est, selon toi, le probleme principal que cet outil veut te montrer ?

Observer s'il comprend : joueur selectionne, observations prioritaires, nature non definitive du signal.

### Tache 2 - retrouver la preuve - 5 min

Demander :

> Tu veux verifier l'observation "Mort sans trade estime". Montre-moi comment tu ferais et raconte ce que tu comprends des faits.

Succes : le participant trouve le round, identifie la fenetre de trade et comprend le niveau de confiance sans aide.

### Tache 3 - lire une zone - 4 min

Afficher Timeline et zones.

Demander :

> Quelle zone te semble la plus problematique ici ? Est-ce que tu consideres cela comme une erreur certaine ? Pourquoi ?

Succes : il identifie la zone et repond qu'il s'agit d'un signal contextuel, pas d'un verdict.

### Tache 4 - utilite - 3 min

Demander :

> Apres cette page, quelle action precise testerais-tu dans ta prochaine partie ?

L'objectif est une action pratique, pas une interpretation parfaite des statistiques.

### Debrief - 2 min

Poser les questions ouvertes :

- Qu'est-ce qui t'a paru le plus utile ?
- Qu'est-ce qui t'a paru inutile, confus ou trop technique ?
- Quelle information attendrais-tu qui manque ?
- Utiliserais-tu cela apres une partie ? Pourquoi ?

## Fiche de prise de notes

| Participant | Profil | T1 comprise | T2 reussie | T3 comprise | Action concrete formulee | Points confus | Citation utile |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | | oui/non | oui/non | oui/non | | | |
| P2 | | oui/non | oui/non | oui/non | | | |
| P3 | | oui/non | oui/non | oui/non | | | |
| P4 | | oui/non | oui/non | oui/non | | | |
| P5 | | oui/non | oui/non | oui/non | | | |

## Criteres de sortie M2

Le jalon UX est valide si :

- 4 participants sur 5 identifient correctement qu'une observation est un signal et non un verdict ;
- 4 sur 5 retrouvent les preuves associees sans aide ;
- 3 sur 5 formulent une action de jeu concrete ;
- aucun meme probleme de comprehension majeur n'apparait chez 2 participants ou plus sans etre corrige dans la maquette.

Si un critere echoue, corriger le langage/le parcours et refaire le test cible avant de commencer le code d'interface.

