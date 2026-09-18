# Decisions de lancement actees

Les choix de base sont maintenant actees. Ils limitent volontairement le premier produit a un perimetre testable et utile.

| Decision | Recommandation v0 | Pourquoi |
| --- | --- | --- |
| Premiere carte | `de_mirage` | Carte largement jouee, facile a tester avec beaucoup de demos |
| Format | Application web locale | Rapide a iterer, sans hebergement ni comptes |
| Cible joueur | Joueur regulier qui analyse ses propres demos | Besoin clair et faible contrainte de partage |
| Donnees | Post-match, fichier local | Simple, compatible fair-play, vie privee |
| Langue | Francais d'abord | Meilleur feedback produit de ton premier cercle |
| Explication | Regles deterministes + preuves | Confiance avant sophistication IA ; IA locale optionnelle plus tard, uniquement pour reformuler |
| Noms d'alertes | "Opportunite de progression" | Evite un jugement excessif |
| Carte 2D | Callouts si fiables, grille sinon | Ne bloque pas le MVP sur des assets parfaits |
| Stockage | Local, suppression manuelle | Aucune obligation serveur au prototype |

## Decisions confirmees

1. Cible : joueur regulier, seul maitre de ses demos locales.
2. Carte pilote : `de_mirage` uniquement.
3. Corpus : 12 demos joueurs recentes, plus 5 demos professionnelles pour la regression technique.
4. Promesse MVP : les quatre analyses H-01 a H-04 avec timeline et preuves par round.
5. Raisonnement : regles explicables ; pas d'IA qui juge librement ni de cout d'API.
6. Direction visuelle : tableau de bord sombre, sobre et classique ; composants accessibles personnalises, sans kit visuel generique.

## Derniers garde-fous avant implementation

1. Constituer le *golden set* : les 50 cas sont maintenant des fixtures automatiques, avec exclusion explicite des rounds knife. La revue visuelle attend le prototype et son bouton de preuve automatique ; elle ne demandera pas de retrouver un joueur manuellement.
2. Verrouiller un asset/source de carte Mirage et ses points de controle geometriques avant de dessiner une vraie carte 2D.
3. Initialiser le depot applicatif seulement apres ces deux controles, en suivant `11_specification_developpement.md`.

Il n'est pas necessaire d'uploader d'autres demos a ce stade.
