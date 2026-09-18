# Regles analytics v0

Ce document est le contrat entre produit et code. Les seuils ci-dessous sont des **hypotheses a calibrer** sur des demos reelles ; ils ne doivent jamais etre caches dans le code.

## Vocabulaire commun

- **Moment** : `(server_tick, subtick)` ; l'ordre s'appuie sur le tick serveur, pas seulement sur une seconde arrondie.
- **Echantillon de position** : position joueur observee dans la demo, avec sa provenance.
- **Zone** : nom de callout/nav-area si disponible ; sinon cellule de grille en coordonnees de carte.
- **Incident** : fait mesurable, relie a un round, une position, des joueurs et un niveau de confiance.
- **Confiance directe** : tiree d'un evenement/etat de demo. **Inferee** : conclusion d'une regle geometrique/temporelle. **Insuffisante** : ne pas produire d'alerte.

## H-01 - Morts sans trade possible

### Question joueur

"Ou est-ce que je meurs sans que mon equipe puisse me venger rapidement ?"

### Donnees minimales

Mort, killer/victime, equipes, positions des coequipiers vivants, ordre temporel des morts.

### Regle v0.1

Pour chaque mort du joueur cible, chercher la mort du tueur par un coequipier dans une fenetre de **5 s**. Le resultat est classe `immediate` (<= 1 s), `timely` (<= 3 s), `late` (<= 5 s) ou `untraded` (aucun trade).

La heatmap comprend les morts `untraded` quand au moins deux coequipiers etaient vivants avant la mort. Le detail algorithmique et les exclusions sont dans `12_contrat_analytique_v0.md`.

### Restitution

"Mort sans trade observe en [zone] : aucun coequipier n'a tue le meme adversaire dans les 5 s. Verifie le timing a deux ou l'utilite disponible avant de reprendre."

### Limites

Ne prouve pas que le mate avait la ligne de vue ou les informations necessaires. Ne pas dire "erreur certaine" ni "mort isolee" tant que le calcul de navigation/visibilite n'est pas implemente.

## H-02 - Positions de premier kill

### Question joueur

"Depuis quelles zones est-ce que je gagne mes premiers duels ?"

### Regle v0

Pour chaque round, identifier le premier `player_death` entre adversaires. Si le joueur cible est killer, retenir sa derniere position fiable juste avant le kill, avec cote (T/CT), arme et zone.

### Restitution

Heatmap de succes : densite ponderee par nombre d'opening kills, avec `n`, rounds et taux de victoire du round. Une zone n'est pas qualifiee de "forte" avant au moins **3 occurrences**.

## H-03 - Position en avantage 5v4

### Question joueur

"Que fais-je quand mon equipe vient de prendre un avantage ?"

### Regle v0

Declencher lorsque le nombre de vivants passe a 5 contre 4 en faveur de l'equipe cible. Echantillonner la position du joueur cible entre **+1 s et +6 s**, uniquement tant que l'avantage 5v4 perdure. Agreger par zone et comparer : morts, degats recus, issue du round.

### Restitution

La carte ne juge pas une position seule. Elle affiche une tendance : "Apres un 5v4, 4 de tes 5 morts surviennent en avancant seul dans [zone]."

## H-04 - Zones de HP perdus

### Question joueur

"Ou est-ce que je prends le plus de degats ?"

### Regle v0

Pour chaque evenement de degats recus par le joueur, utiliser sa position au moment du dommage ou le plus recent echantillon fiable. Agreger `hp_damage` et le nombre d'impacts par zone/cellule, avec filtres T/CT, arme adverse et phase du round.

### Restitution

Deux modes : somme de HP perdus (impact total) et HP moyen par passage (danger relatif). Toujours montrer l'effectif : 80 HP sur 1 passage n'a pas le meme sens que 80 HP sur 12 passages.

## O-01 - Achat incoherent (phase 2)

Condition de base a definir avec un arbre de decision documente : argent equipe, valeur d'equipement, cote, resultat des rounds precedents et objectif d'achat equipe. Avant de l'afficher, valider manuellement au moins 30 rounds d'eco.

## O-02 - Timing de reprise isolee (phase 2)

Condition de base : entree du joueur dans une zone de reprise plus de `X` secondes avant le premier coequipier, suivie d'un dommage ou d'une mort. Necessite nav mesh/callouts fiables et validation video/demo.

## Regles explicitement reportees

- "Ton crosshair etait trop loin" : exige une modelisation des angles probables, de l'occlusion et une confiance insuffisante au MVP.
- "Ton flank etait visible" : exige une ligne de vue, une geometrie de carte et la distinction demo/vision client.
- "Tu aurais du faire X" : depend des communications et de l'intention ; uniquement comme suggestion humaine future.
