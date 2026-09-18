# Systeme de design - CS2 Round Analyzer v0

## Decision verrouillee

Le produit adopte un **dashboard classique, sombre et sobre**. Il privilegie la lecture de donnees, l'ordre visuel et la preuve, plutot qu'une identite esport agressive ou un style decoratif.

Les deux ecrans de reference sont les maquettes validees en conversation :

- Vue d'ensemble.
- Timeline et zones.

Ces maquettes donnent la direction produit. Les chiffres et noms qui y figurent sont des donnees d'exemple et ne constituent pas encore un rapport reel.

## Principes non negociables

1. **Une question par zone d'ecran.** Une carte ou un panneau ne melange pas score, conseil et diagnostic.
2. **La preuve est toujours accessible.** Toute observation affiche round, evenement(s) source(s), niveau de confiance et lien vers son contexte.
3. **La couleur signale, elle ne decore pas.** Le bleu sert a la selection et aux donnees actives ; l'orange est reserve aux signaux a examiner.
4. **Les surfaces sont discretes.** Bordures fines, rayons modestes, pas d'ombres lourdes ni de glassmorphism.
5. **Le texte est factuel.** "Trade non observe" est preferable a "erreur de placement".
6. **La densite reste maitrisee.** Le lecteur doit pouvoir parcourir une page complete sans defilement horizontal, a partir de 320 px de largeur.

## Fondations visuelles

| Token semantique | Usage | Regle |
| --- | --- | --- |
| `surface-base` | Arriere-plan de l'application | Charbon tres sombre en theme dark |
| `surface-raised` | En-tetes, panneaux, inputs | Un seul niveau au-dessus du fond |
| `surface-muted` | Etat non actif, details secondaires | Ne jamais diminuer la lisibilite |
| `content-primary` | Titres, valeurs, actions | Contraste eleve |
| `content-secondary` | Metadonnees et explications | Jamais pour une information obligatoire |
| `border-subtle` | Separation de structure | Fine et peu contrastée |
| `accent-primary` | Selection, navigation active, round cible | Bleu desature, usage rare |
| `accent-warning` | Signal a examiner, danger contextuel | Orange desature, jamais seul indice |

La police de base est la police systeme sans-serif. Les nombres de score, tick et HP utilisent des chiffres tabulaires pour rester alignes.

## Bibliotheque et composants

**React Aria Components** gere les comportements accessibles et le clavier. Notre projet definit le rendu de chaque composant avec ses tokens propres : aucun theme cle-en-main n'est importe.

| Composant | Role | Etats minimaux |
| --- | --- | --- |
| `AppShell` | Barre haute, navigation laterale, contenu | desktop, mobile |
| `SidebarNav` | Navigation de rapport | normal, actif, focus, mobile scrollable |
| `MatchSelector` | Choix du match/joueur | vide, ouvert, selectionne, erreur |
| `MetricStrip` | Stats prioritaires | chargement, valeur, indisponible |
| `Panel` | Conteneur fonctionnel | normal, vide, chargement, erreur |
| `InsightRow` | Une observation de coaching | normal, actif, confiance directe/inferee |
| `RoundStrip` | Navigation par round | gagne, perdu, actif, avec signal |
| `TimelineEvent` | Evenement temporel | normal, actif, information, alerte |
| `EvidencePanel` | Faits sources d'une observation | charge, donnees insuffisantes |
| `ZoneGrid` | Vue de densite par zone | vide, selectionnee, intensite 0-3 |
| `FilterGroup` | Cote, type de signal, phase de round | normal, actif, desactive |

## Contrats d'interaction

### Observation -> preuve

1. Le clic sur une `InsightRow` selectionne l'observation.
2. La `RoundStrip` se cale sur le round associe.
3. La `TimelineEvent` source devient active.
4. L'`EvidencePanel` explique la regle, les valeurs, la confiance et les limites.
5. La zone concernee est selectionnee dans `ZoneGrid` ou plus tard sur la carte 2D reelle.

Ce parcours ne depend pas d'animations ; l'etat doit changer immediatement et rester lisible au clavier.

### Donnees insuffisantes

Un composant ne disparait pas sans explication. Il affiche :

> Pas assez de donnees fiables pour produire ce resultat sur cette demo.

Le produit n'invente ni une heatmap, ni une recommandation de remplacement.

## Accessibilite attendue

- Toutes les actions sont des elements natifs ou des composants React Aria equivalents.
- Focus visible uniquement pour la navigation clavier, jamais supprime.
- Toute couleur est accompagnee par texte, icone ou libelle.
- Les timelines et grilles de rounds donnent un nom accessible comprenant le numero, l'issue et l'etat de selection.
- Les panneaux de details utilisent `aria-live="polite"` lors d'un changement de selection.

## Hors direction artistique

- Pas de neon, de fond e-sport bruyant ni de skins de carte decoratifs.
- Pas de grille de cartes KPI repetitives pour remplir l'espace.
- Pas de score global opaque du type "tu as joue 7,4/10".
- Pas de micro-animation autonome ou de compteur anime.
- Pas de badge de statut lorsque du texte normal suffit.
