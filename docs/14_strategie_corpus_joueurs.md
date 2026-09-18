# Strategie de corpus - joueurs cibles

## Decision

Les cinq demos Vitality/Mirage ne servent qu'a verifier le format, les performances du parser, la presence des evenements et la robustesse multi-build. Elles **ne definissent pas la norme de bon jeu** et ne doivent pas calibrer durablement les messages de coaching.

Les seuils issus de ce corpus sont etiquetes `provisional_technical` jusqu'a validation sur des joueurs comparables a la cible du produit.

## Cible a echantillonner pour le MVP

Joueur regulier qui joue principalement en solo/duo, souhaite progresser apres ses matchs et est capable de comprendre les notions de trade, eco et position. Le premier produit ne cherche pas a coacher un professionnel ni un debutant complet.

La plage exacte de niveau est recueillie en metadata, mais ne sert pas encore a classer/afficher le joueur. Elle servira uniquement a detecter si les seuils varient fortement avec le niveau.

## Lot de calibration recu : 12 demos Mirage

Le premier lot recu couvre :

- **12 demos completes de_mirage**, toutes verifiees par parser ;
- 3 Premier 15--20k, dont les trois matchs de Sobek ;
- 3 FACEIT 10, 2 FACEIT 7 et 4 FACEIT 3 ;
- des matchs fournis comme datant de moins d'une semaine ;
- 104 participants distincts observes de maniere pseudonyme dans les demos ;
- aucun vocal/chat n'est analyse ni conserve dans le MVP.

Deux demos FACEIT 3 contiennent 11 joueurs dans les informations de la demo, probablement a cause d'un remplacement ou d'un enregistrement supplementaire. Ce n'est pas bloquant : les calculs utilisent l'etat vivant par tick et non l'hypothese rigide de 10 identites.

Ce lot est suffisant pour verifier les distributions et les faux positifs. Ne pas uploader d'autres demos Mirage avant la revue manuelle des incidents : nous saurons alors exactement quelle lacune de donnees combler.

## Metadata minimale accompagnee de chaque demo

| Champ | Exemple | Usage |
| --- | --- | --- |
| Joueur cible | pseudonyme local | regrouper les demos sans exposer SteamID |
| Niveau approximatif | Premier 15k / FACEIT 5 | segmenter les resultats en interne |
| Source | Premiere / FACEIT | identifier les differences de format |
| Date approximative | 2026-09 | suivre les patchs |
| Role habituel (optionnel) | rifler / AWP / mixte | future analyse, pas de seuil v0.1 |

Les identifiants Steam bruts ne sont pas necessaires dans ce tableau.

## Utilisation du lot de 12

1. Parser les 12 fichiers et verifier le contrat technique.
2. Generer tous les candidats H-01 a H-04 sans les afficher a des utilisateurs.
3. Etiqueter manuellement un echantillon de 50 incidents : 20 trades, 10 non-trades, 10 opening kills, 5 fenetres 5v4, 5 dommages/positions.
4. Marquer chaque incident : correct, correct mais incomplet, faux positif, donnees insuffisantes.
5. Comparer les delais de trade et l'equilibre des resultats avec le corpus professionnel.
6. Conserver les seuils si la variation est faible ; sinon choisir des seuils adaptes a la cible ou des segments de niveau explicites.

## Quand demander plus de demos

| Question | Ajout requis |
| --- | --- |
| Valider Mirage pour la beta | 30 a 50 demos cibles, au moins 10 joueurs |
| Ajouter une nouvelle carte | 8 a 12 demos de cette carte + 12 points de validation geometrique |
| Comparer deux niveaux | 15 demos minimum par segment |
| Ajouter une regle de coaching nouvelle | 20 a 30 exemples manuellement etiquetes de cette situation |
| Construire un modele ML | Au moins plusieurs centaines de demos anonymisees, apres validation produit |

## Telechargement automatique : decision prudente

Pour le prototype, nous privilegions **l'import manuel de fichiers que le joueur possede ou est autorise a utiliser**. Par exemple, FACEIT documente le telechargement manuel depuis la page d'un match recent.

Nous ne construisons pas de scraper ou d'automatisation de telechargement maintenant, car il faudrait au minimum :

- une API ou une autorisation officielle documentee par la source ;
- un consentement clair du titulaire du compte pour les donnees de ses matchs ;
- des limites de debit et une retention minimale ;
- une verification des conditions de la plateforme et du droit de redistribution.

Une future integration peut commencer par une source qui autorise officiellement l'acces aux **propres** matchs d'un utilisateur. Elle restera un connecteur opt-in, jamais un collecteur de demos publiques a grande echelle.

## Separation de corpus

```text
corpus_technique/
  5 demos professionnelles Mirage
  but : parser, regression, compatibilite build

corpus_cible/
  demos de joueurs reguliers Mirage
  but : calibrage des seuils, faux positifs, utilite coaching

corpus_extension/
  nouvelles cartes et nouveaux segments de niveau
  but : generalisation uniquement apres MVP Mirage
```
