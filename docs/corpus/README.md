# Protocole de validation du corpus Vitality / Mirage

## Etat

Le lot initial contient cinq demos CS2 Mirage impliquees avec Vitality. Toutes sont valides au niveau conteneur (`PBDEMS2`) et verrouillees par empreinte SHA-256 dans [`manifest.v0.yml`](manifest.v0.yml).

Ce corpus est excellent pour demarrer le pilote `de_mirage`, mais il a un biais assume : matchs professionnels, une seule carte et probablement un nombre limite de versions de jeu. Il ne doit pas servir a conclure que le produit fonctionne pour toutes les demos publiques.

## Fiche manuelle par demo

Avant d'utiliser le corpus pour calibrer une regle, une fiche est remplie depuis le replay CS2 ou une source fiable :

| Champ | Exemple |
| --- | --- |
| Score final / nombre de rounds | 13-10 / 23 rounds |
| Joueurs et equipes | Vitality, adversaire, cinq joueurs chacun |
| Cinq morts de reference | round, joueur, killer, moment approximatif, zone |
| Cinq dommages recus | round, victime, attaquant, arme, HP |
| Trois fenetres 5v4 | round, equipe avant, moment, issue du round |
| Trois opening duels | round, killer, victime, zone, issue du round |

La fiche ne doit pas etre remplie par l'IA. Elle est notre oracle independant pour savoir si le code reconstruit correctement les faits.

## Premiere passe de faisabilite

Quand `demoparser2` est disponible dans l'environnement de travail, executer un script temporaire qui, pour chaque demo :

1. lit carte, participants, nombre de rounds et score final ;
2. compte les kills et les dommages ;
3. extrait les positions et l'etat vivant/mort de chaque joueur ;
4. compare ces resultats aux fiches manuelles ;
5. consigne toute donnee manquante ou anomalie.

**Porte de sortie :** le parser doit extraire de facon coherente les donnees necessaires a H-01, H-02, H-03 et H-04. Sinon, nous adaptons la promesse du MVP avant d'ecrire son interface.

